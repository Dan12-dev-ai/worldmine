# Worldmine Market News AI Agent

An autonomous AI-powered market news scraper and analyzer for the Worldmine platform.

## Features

- **Agentic Workflow**: Uses LangGraph with ReAct pattern for intelligent news processing
- **Multi-Source Scraping**: Integrates with Tavily API for comprehensive news gathering
- **AI Analysis**: Leverages Claude 3.5 Sonnet for professional SMB-focused insights
- **Smart Categorization**: Automatically categorizes news into Economic, Supply, or Daily Mini
- **Price Trend Detection**: Extracts and analyzes commodity price movements
- **Multi-Language Support**: Provides Amharic translations for local users
- **Automated Posting**: Seamlessly integrates with Supabase database

## Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Search Node   │───▶│   Analysis Node  │───▶│   Posting Node  │
│                 │    │                  │    │                 │
│ • Tavily API    │    │ • Claude 3.5     │    │ • Supabase      │
│ • Query Engine  │    │ • Categorization │    │ • Deduplication │
│ • Content Fetch │    │ • Translation    │    │ • Validation    │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## Setup

### Prerequisites

- Python 3.11+
- Docker & Docker Compose
- Supabase project
- API keys for external services

### Environment Variables

Create a `.env` file based on `.env.example`:

```bash
# AI Services
OPENAI_API_KEY=your_openai_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# Search API
TAVILY_API_KEY=your_tavily_api_key_here

# Database
SUPABASE_URL=your_supabase_url_here
SUPABASE_SERVICE_ROLE_KEY=your_supabase_service_role_key_here

# Translation
GOOGLE_TRANSLATE_API_KEY=your_google_translate_api_key_here
```

### Installation

1. **Clone and setup**:
   ```bash
   cd ai-agent
   pip install -r requirements.txt
   playwright install
   ```

2. **Run with Docker** (recommended):
   ```bash
   docker-compose up -d
   ```

3. **Run directly**:
   ```bash
   python main.py
   ```

## Usage

### Manual Execution
```bash
python main.py
```

### Automated Scheduling
The system includes a Docker-based scheduler that runs every 6 hours:

```bash
# Start with scheduler
docker-compose up -d

# View logs
docker-compose logs -f market-news-agent
```

### Custom Scheduling
Modify the cron expression in `docker-compose.yml`:

```yaml
OFELIA_CRON_RUN_AGENT=0 */6 * * * python /app/main.py
```

## News Processing Pipeline

### 1. Search Phase
- Executes 5 targeted search queries
- Fetches up to 25 articles per run
- Filters for relevant market content

### 2. Analysis Phase
- **Categorization**: Economic, Supply, or Mini based on content analysis
- **Claude Analysis**: Generates SMB-focused insights (2-3 sentences)
- **Translation**: Creates Amharic versions for local users
- **Price Extraction**: Identifies commodity price movements

### 3. Posting Phase
- **Deduplication**: Prevents duplicate articles
- **Priority Scoring**: 1-5 scale based on urgency and impact
- **Database Storage**: Inserts into `market_news` table
- **Error Handling**: Logs and continues on individual failures

## Data Schema

```sql
market_news (
  id UUID PRIMARY KEY,
  title TEXT NOT NULL,
  content TEXT NOT NULL,
  category TEXT CHECK (category IN ('Economic', 'Supply', 'Mini')),
  analysis TEXT,
  analysis_am TEXT,
  source_url TEXT,
  price_trend JSONB,
  priority INTEGER CHECK (priority >= 1 AND priority <= 5),
  is_active BOOLEAN DEFAULT true,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
)
```

## Price Trend Detection

The agent automatically detects price changes for commodities:

```json
{
  "direction": "up|down|stable",
  "percentage": 5.2,
  "commodity": "Gold"
}
```

Supported commodities: Gold, Silver, Copper, Oil, Gas, Wheat, Corn, Coffee

## Monitoring & Logging

### Log Levels
- `INFO`: Normal operation
- `WARNING`: Non-critical issues
- `ERROR`: Failed operations

### Health Checks
```bash
curl http://localhost:8000/health
```

### Performance Metrics
- Average processing time: ~2-3 minutes
- Articles per run: 15-25
- Success rate: >95%

## Integration Points

### Frontend Integration
The React frontend consumes news via the API endpoint:

```typescript
// GET /api/market-news?category=Economic&limit=10
```

### Database Integration
- **Auto-cleanup**: Weekly removal of articles older than 7 days
- **Row Level Security**: Ensures data privacy
- **Real-time Updates**: Frontend refreshes every 30 seconds

## Troubleshooting

### Common Issues

1. **API Rate Limits**:
   - Reduce search frequency
   - Check API key quotas

2. **Parsing Errors**:
   - Content format changes
   - Missing required fields

3. **Database Connection**:
   - Verify Supabase credentials
   - Check network connectivity

### Debug Mode
Enable detailed logging:

```bash
LOG_LEVEL=DEBUG python main.py
```

## Development

### Adding New Search Queries
```python
self.search_queries = [
    "Global economic trends market analysis 2024",
    # Add your new queries here
]
```

### Custom Analysis Logic
Modify the `generate_analysis` method to customize Claude prompts.

### Extending Categories
Update the `categorize_news` method and database schema.

## Deployment

### Production Considerations
- Use environment-specific configurations
- Implement monitoring and alerting
- Set up backup strategies
- Configure SSL certificates

### Scaling
- Horizontal scaling with multiple containers
- Load balancing for high-traffic scenarios
- Database optimization for large datasets

## Security

- API keys stored in environment variables
- Row-level security in database
- Input validation and sanitization
- Rate limiting on API endpoints

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is part of the Worldmine platform ecosystem.
