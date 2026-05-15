"""
Brotli Compression Middleware for DEDAN 2.0
High-performance compression with 20% smaller payloads
"""

import asyncio
import logging
import time
from typing import Callable, Optional
import brotli
from fastapi import Request, Response
from fastapi.middleware.base import BaseHTTPMiddleware
from starlette.responses import StreamingResponse
import zlib
import gzip
from dataclasses import dataclass
from enum import Enum

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class CompressionAlgorithm(Enum):
    """Compression algorithms"""
    BROTLI = "brotli"
    GZIP = "gzip"
    NONE = "none"

@dataclass
class CompressionConfig:
    """Compression configuration"""
    enabled: bool = True
    algorithm: CompressionAlgorithm = CompressionAlgorithm.BROTLI
    min_size: int = 1024  # Minimum size to compress
    quality: int = 4  # Brotli quality (0-11, 4 is default)
    lgwin: int = 22  # Brotli window size
    gzip_level: int = 6  # Gzip compression level (1-9)
    chunk_size: int = 16384  # Chunk size for streaming
    buffer_size: int = 8192  # Buffer size for compression
    enable_streaming: bool = True
    enable_adaptive: bool = True
    adaptive_threshold: float = 0.8  # Threshold for adaptive compression

class BrotliCompressionMiddleware(BaseHTTPMiddleware):
    """Brotli compression middleware for FastAPI"""
    
    def __init__(self, app, config: Optional[CompressionConfig] = None):
        super().__init__(app)
        self.config = config or CompressionConfig()
        self.compressor = None
        self.decompressor = None
        self.stats = {
            'requests_processed': 0,
            'responses_compressed': 0,
            'bytes_saved': 0,
            'compression_time_ms': 0,
            'brotli_compressions': 0,
            'gzip_compressions': 0,
            'adaptive_compressions': 0
        }
        
        # Initialize compression engines
        self._initialize_compressors()
    
    def _initialize_compressors(self):
        """Initialize compression engines"""
        try:
            # Initialize Brotli compressor
            self.compressor = brotli.Compressor(
                quality=self.config.quality,
                lgwin=self.config.lgwin,
                mode=brotli.Mode.GENERIC
            )
            
            # Initialize Brotli decompressor
            self.decompressor = brotli.Decompressor()
            
            logger.info(f"Initialized Brotli compressor: quality={self.config.quality}, lgwin={self.config.lgwin}")
            
        except Exception as e:
            logger.error(f"Failed to initialize compressors: {e}")
            raise
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request and apply compression"""
        start_time = time.time()
        
        try:
            # Process the request
            response = await call_next(request)
            
            # Update stats
            self.stats['requests_processed'] += 1
            
            # Determine if compression should be applied
            if self._should_compress(request, response):
                compressed_response = await self._compress_response(response)
                
                # Update compression stats
                self.stats['responses_compressed'] += 1
                self.stats['bytes_saved'] += self._calculate_bytes_saved(response, compressed_response)
                self.stats['compression_time_ms'] += (time.time() - start_time) * 1000
                
                if self.config.algorithm == CompressionAlgorithm.BROTLI:
                    self.stats['brotli_compressions'] += 1
                elif self.config.algorithm == CompressionAlgorithm.GZIP:
                    self.stats['gzip_compressions'] += 1
                
                logger.debug(f"Compressed response: {response.headers.get('content-length', 0)} -> {compressed_response.headers.get('content-length', 0)} bytes")
                
                return compressed_response
            else:
                return response
                
        except Exception as e:
            logger.error(f"Error in compression middleware: {e}")
            return await call_next(request)
    
    def _should_compress(self, request: Request, response: Response) -> bool:
        """Determine if response should be compressed"""
        if not self.config.enabled:
            return False
        
        # Check if response is compressible
        content_type = response.headers.get('content-type', '')
        if not self._is_compressible_content_type(content_type):
            return False
        
        # Check if response is already compressed
        content_encoding = response.headers.get('content-encoding', '')
        if content_encoding:
            return False
        
        # Check response size
        content_length = response.headers.get('content-length')
        if content_length and int(content_length) < self.config.min_size:
            return False
        
        # Check if client accepts compression
        accept_encoding = request.headers.get('accept-encoding', '')
        if not self._client_accepts_encoding(accept_encoding):
            return False
        
        # Check if adaptive compression should be used
        if self.config.enable_adaptive:
            return self._should_use_adaptive_compression(request, response)
        
        return True
    
    def _is_compressible_content_type(self, content_type: str) -> bool:
        """Check if content type is compressible"""
        compressible_types = [
            'text/html',
            'text/css',
            'text/javascript',
            'application/javascript',
            'application/json',
            'application/xml',
            'text/xml',
            'text/plain',
            'application/wasm',
            'image/svg+xml',
            'application/x-font-ttf',
            'application/x-font-opentype',
            'application/font-woff',
            'application/font-woff2'
        ]
        
        # Remove charset and other parameters
        base_type = content_type.split(';')[0].strip().lower()
        
        return any(base_type.startswith(ct) for ct in compressible_types)
    
    def _client_accepts_encoding(self, accept_encoding: str) -> bool:
        """Check if client accepts our compression algorithm"""
        if not accept_encoding:
            return False
        
        accept_encoding_lower = accept_encoding.lower()
        
        if self.config.algorithm == CompressionAlgorithm.BROTLI:
            return 'br' in accept_encoding_lower or 'brotli' in accept_encoding_lower
        elif self.config.algorithm == CompressionAlgorithm.GZIP:
            return 'gzip' in accept_encoding_lower or 'deflate' in accept_encoding_lower
        
        return False
    
    def _should_use_adaptive_compression(self, request: Request, response: Response) -> bool:
        """Determine if adaptive compression should be used"""
        # Check if response size is above threshold
        content_length = response.headers.get('content-length')
        if content_length:
            size_mb = int(content_length) / (1024 * 1024)
            if size_mb > self.config.adaptive_threshold:
                return True
        
        # Check if request is from a mobile client (might prefer faster compression)
        user_agent = request.headers.get('user-agent', '').lower()
        mobile_indicators = ['mobile', 'android', 'iphone', 'ipad', 'tablet']
        if any(indicator in user_agent for indicator in mobile_indicators):
            return True
        
        # Check if connection is slow
        # This would be determined from request context or headers
        # For now, return False to avoid over-compression
        return False
    
    async def _compress_response(self, response: Response) -> Response:
        """Compress response based on algorithm"""
        if self.config.algorithm == CompressionAlgorithm.BROTLI:
            return await self._compress_with_brotli(response)
        elif self.config.algorithm == CompressionAlgorithm.GZIP:
            return await self._compress_with_gzip(response)
        else:
            return response
    
    async def _compress_with_brotli(self, response: Response) -> Response:
        """Compress response using Brotli"""
        try:
            # Get response content
            if hasattr(response, 'body'):
                content = response.body
            elif hasattr(response, 'content'):
                content = response.content
            else:
                return response
            
            # Convert to bytes if needed
            if isinstance(content, str):
                content = content.encode('utf-8')
            
            # Compress content
            compressed_data = self._compress_data_brotli(content)
            
            # Create new response with compressed content
            compressed_response = Response(
                content=compressed_data,
                status_code=response.status_code,
                headers=dict(response.headers),
                media_type=response.media_type
            )
            
            # Set compression headers
            compressed_response.headers['content-encoding'] = 'br'
            compressed_response.headers['content-length'] = str(len(compressed_data))
            
            # Add Vary header for caches
            if 'vary' not in compressed_response.headers:
                compressed_response.headers['vary'] = 'Accept-Encoding'
            
            # Add compression metrics
            compressed_response.headers['x-compression-algorithm'] = 'brotli'
            compressed_response.headers['x-compression-ratio'] = str(len(compressed_data) / len(content) if content else 1)
            
            self.stats['adaptive_compressions'] += 1
            
            return compressed_response
            
        except Exception as e:
            logger.error(f"Error compressing with Brotli: {e}")
            return response
    
    async def _compress_with_gzip(self, response: Response) -> Response:
        """Compress response using Gzip"""
        try:
            # Get response content
            if hasattr(response, 'body'):
                content = response.body
            elif hasattr(response, 'content'):
                content = response.content
            else:
                return response
            
            # Convert to bytes if needed
            if isinstance(content, str):
                content = content.encode('utf-8')
            
            # Compress content
            compressed_data = self._compress_data_gzip(content)
            
            # Create new response with compressed content
            compressed_response = Response(
                content=compressed_data,
                status_code=response.status_code,
                headers=dict(response.headers),
                media_type=response.media_type
            )
            
            # Set compression headers
            compressed_response.headers['content-encoding'] = 'gzip'
            compressed_response.headers['content-length'] = str(len(compressed_data))
            
            # Add Vary header for caches
            if 'vary' not in compressed_response.headers:
                compressed_response.headers['vary'] = 'Accept-Encoding'
            
            # Add compression metrics
            compressed_response.headers['x-compression-algorithm'] = 'gzip'
            compressed_response.headers['x-compression-ratio'] = str(len(compressed_data) / len(content) if content else 1)
            
            return compressed_response
            
        except Exception as e:
            logger.error(f"Error compressing with Gzip: {e}")
            return response
    
    def _compress_data_brotli(self, data: bytes) -> bytes:
        """Compress data using Brotli"""
        if not data:
            return b''
        
        try:
            # Reset compressor
            self.compressor.flush()
            
            # Check if streaming should be used
            if self.config.enable_streaming and len(data) > self.config.chunk_size:
                return self._compress_streaming_brotli(data)
            else:
                # Compress in one go
                compressed = self.compressor.compress(data)
                return compressed
                
        except Exception as e:
            logger.error(f"Brotli compression error: {e}")
            return data
    
    def _compress_streaming_brotli(self, data: bytes) -> bytes:
        """Compress data using streaming Brotli"""
        compressed_chunks = []
        
        try:
            # Process data in chunks
            for i in range(0, len(data), self.config.chunk_size):
                chunk = data[i:i + self.config.chunk_size]
                compressed_chunk = self.compressor.compress(chunk)
                compressed_chunks.append(compressed_chunk)
            
            # Finalize compression
            final_chunk = self.compressor.flush()
            if final_chunk:
                compressed_chunks.append(final_chunk)
            
            return b''.join(compressed_chunks)
            
        except Exception as e:
            logger.error(f"Streaming Brotli compression error: {e}")
            return data
    
    def _compress_data_gzip(self, data: bytes) -> bytes:
        """Compress data using Gzip"""
        if not data:
            return b''
        
        try:
            # Check if streaming should be used
            if self.config.enable_streaming and len(data) > self.config.chunk_size:
                return self._compress_streaming_gzip(data)
            else:
                # Compress in one go
                return zlib.compress(data, self.config.gzip_level)
                
        except Exception as e:
            logger.error(f"Gzip compression error: {e}")
            return data
    
    def _compress_streaming_gzip(self, data: bytes) -> bytes:
        """Compress data using streaming Gzip"""
        compressed_chunks = []
        
        try:
            # Create streaming compressor
            compressor = zlib.compressobj(self.config.gzip_level, zlib.DEFLATED, -zlib.MAX_WBITS)
            
            # Process data in chunks
            for i in range(0, len(data), self.config.chunk_size):
                chunk = data[i:i + self.config.chunk_size]
                compressed_chunk = compressor.compress(chunk)
                compressed_chunks.append(compressed_chunk)
            
            # Finalize compression
            final_chunk = compressor.flush()
            if final_chunk:
                compressed_chunks.append(final_chunk)
            
            return b''.join(compressed_chunks)
            
        except Exception as e:
            logger.error(f"Streaming Gzip compression error: {e}")
            return data
    
    def _calculate_bytes_saved(self, original_response: Response, compressed_response: Response) -> int:
        """Calculate bytes saved by compression"""
        original_size = int(original_response.headers.get('content-length', 0))
        compressed_size = int(compressed_response.headers.get('content-length', 0))
        
        return max(0, original_size - compressed_size)
    
    def get_compression_stats(self) -> dict:
        """Get compression statistics"""
        total_requests = self.stats['requests_processed']
        compressed_responses = self.stats['responses_compressed']
        
        if total_requests > 0:
            compression_rate = (compressed_responses / total_requests) * 100
        else:
            compression_rate = 0
        
        return {
            'total_requests': total_requests,
            'compressed_responses': compressed_responses,
            'compression_rate': compression_rate,
            'total_bytes_saved': self.stats['bytes_saved'],
            'avg_compression_time_ms': self.stats['compression_time_ms'] / max(1, compressed_responses),
            'brotli_compressions': self.stats['brotli_compressions'],
            'gzip_compressions': self.stats['gzip_compressions'],
            'adaptive_compressions': self.stats['adaptive_compressions'],
            'algorithm': self.config.algorithm.value,
            'enabled': self.config.enabled
        }
    
    def reset_stats(self) -> None:
        """Reset compression statistics"""
        self.stats = {
            'requests_processed': 0,
            'responses_compressed': 0,
            'bytes_saved': 0,
            'compression_time_ms': 0,
            'brotli_compressions': 0,
            'gzip_compressions': 0,
            'adaptive_compressions': 0
        }

class AdaptiveCompressionMiddleware(BrotliCompressionMiddleware):
    """Adaptive compression middleware that chooses best algorithm"""
    
    def __init__(self, app, config: Optional[CompressionConfig] = None):
        super().__init__(app, config)
        self.algorithm_stats = {
            'brotli': {'compression_ratio': 0, 'time_ms': 0, 'count': 0},
            'gzip': {'compression_ratio': 0, 'time_ms': 0, 'count': 0}
        }
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request with adaptive compression"""
        start_time = time.time()
        
        try:
            # Process the request
            response = await call_next(request)
            
            # Update stats
            self.stats['requests_processed'] += 1
            
            # Determine if compression should be applied
            if not self._should_compress(request, response):
                return response
            
            # Choose best compression algorithm
            best_algorithm = await self._choose_best_algorithm(request, response)
            
            # Temporarily update config for this request
            original_algorithm = self.config.algorithm
            self.config.algorithm = best_algorithm
            
            # Apply compression
            compressed_response = await self._compress_response(response)
            
            # Restore original config
            self.config.algorithm = original_algorithm
            
            # Update algorithm stats
            compression_time = (time.time() - start_time) * 1000
            if best_algorithm == CompressionAlgorithm.BROTLI:
                self.algorithm_stats['brotli']['count'] += 1
                self.algorithm_stats['brotli']['time_ms'] += compression_time
                compression_ratio = float(compressed_response.headers.get('x-compression-ratio', 1))
                self.algorithm_stats['brotli']['compression_ratio'] += compression_ratio
            elif best_algorithm == CompressionAlgorithm.GZIP:
                self.algorithm_stats['gzip']['count'] += 1
                self.algorithm_stats['gzip']['time_ms'] += compression_time
                compression_ratio = float(compressed_response.headers.get('x-compression-ratio', 1))
                self.algorithm_stats['gzip']['compression_ratio'] += compression_ratio
            
            # Update overall compression stats
            self.stats['responses_compressed'] += 1
            self.stats['bytes_saved'] += self._calculate_bytes_saved(response, compressed_response)
            self.stats['compression_time_ms'] += compression_time
            
            logger.debug(f"Adaptive compression: {best_algorithm.value} chosen")
            
            return compressed_response
            
        except Exception as e:
            logger.error(f"Error in adaptive compression middleware: {e}")
            return await call_next(request)
    
    async def _choose_best_algorithm(self, request: Request, response: Response) -> CompressionAlgorithm:
        """Choose best compression algorithm based on context"""
        accept_encoding = request.headers.get('accept-encoding', '').lower()
        
        # Check what client accepts
        accepts_brotli = 'br' in accept_encoding or 'brotli' in accept_encoding
        accepts_gzip = 'gzip' in accept_encoding or 'deflate' in accept_encoding
        
        if accepts_brotli and accepts_gzip:
            # Client accepts both, choose based on performance
            return self._choose_by_performance()
        elif accepts_brotli:
            return CompressionAlgorithm.BROTLI
        elif accepts_gzip:
            return CompressionAlgorithm.GZIP
        else:
            # Client doesn't accept compression, choose based on content
            return self._choose_by_content_type(response)
    
    def _choose_by_performance(self) -> CompressionAlgorithm:
        """Choose algorithm based on historical performance"""
        brotli_stats = self.algorithm_stats['brotli']
        gzip_stats = self.algorithm_stats['gzip']
        
        if brotli_stats['count'] == 0:
            return CompressionAlgorithm.BROTLI  # Default to Brotli
        
        if gzip_stats['count'] == 0:
            return CompressionAlgorithm.GZIP
        
        # Calculate average compression ratios
        brotli_ratio = brotli_stats['compression_ratio'] / brotli_stats['count']
        gzip_ratio = gzip_stats['compression_ratio'] / gzip_stats['count']
        
        # Calculate average compression times
        brotli_time = brotli_stats['time_ms'] / brotli_stats['count']
        gzip_time = gzip_stats['time_ms'] / gzip_stats['count']
        
        # Choose based on better compression ratio and speed
        if brotli_ratio > gzip_ratio and brotli_time <= gzip_time * 1.2:
            return CompressionAlgorithm.BROTLI
        elif gzip_ratio > brotli_ratio * 1.1 or gzip_time < brotli_time * 0.8:
            return CompressionAlgorithm.GZIP
        else:
            return CompressionAlgorithm.BROTLI  # Default to Brotli
    
    def _choose_by_content_type(self, response: Response) -> CompressionAlgorithm:
        """Choose algorithm based on content type"""
        content_type = response.headers.get('content-type', '').lower()
        
        # Brotli is better for text-based content
        if any(ct in content_type for ct in ['text/', 'application/json', 'application/xml']):
            return CompressionAlgorithm.BROTLI
        # Gzip might be better for binary content
        elif any(ct in content_type for ct in ['application/wasm', 'application/octet-stream']):
            return CompressionAlgorithm.GZIP
        else:
            return CompressionAlgorithm.BROTLI  # Default to Brotli
    
    def get_algorithm_stats(self) -> dict:
        """Get algorithm performance statistics"""
        stats = {}
        
        for algorithm, algorithm_stats in self.algorithm_stats.items():
            if algorithm_stats['count'] > 0:
                stats[algorithm] = {
                    'count': algorithm_stats['count'],
                    'avg_compression_ratio': algorithm_stats['compression_ratio'] / algorithm_stats['count'],
                    'avg_compression_time_ms': algorithm_stats['time_ms'] / algorithm_stats['count']
                }
            else:
                stats[algorithm] = {
                    'count': 0,
                    'avg_compression_ratio': 0,
                    'avg_compression_time_ms': 0
                }
        
        return stats

# Factory functions
def create_brotli_middleware(app, config: Optional[CompressionConfig] = None) -> BrotliCompressionMiddleware:
    """Create Brotli compression middleware"""
    return BrotliCompressionMiddleware(app, config)

def create_adaptive_compression_middleware(app, config: Optional[CompressionConfig] = None) -> AdaptiveCompressionMiddleware:
    """Create adaptive compression middleware"""
    return AdaptiveCompressionMiddleware(app, config)

# Example usage
async def example_usage():
    """Example usage of compression middleware"""
    from fastapi import FastAPI
    
    # Create FastAPI app
    app = FastAPI()
    
    # Configure compression
    config = CompressionConfig(
        enabled=True,
        algorithm=CompressionAlgorithm.BROTLI,
        quality=4,
        min_size=1024,
        enable_streaming=True,
        enable_adaptive=True
    )
    
    # Add compression middleware
    app.add_middleware(create_brotli_middleware, config)
    
    @app.get("/test")
    async def test_endpoint():
        return {"message": "This is a test response for compression", "data": "x" * 1000}
    
    print("Compression middleware configured and ready!")

if __name__ == "__main__":
    asyncio.run(example_usage())
