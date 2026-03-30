# Worldmine Performance Testing with k6

This directory contains performance testing scripts for the Worldmine platform using Grafana k6.

## 🚀 Quick Start

### Prerequisites
- Install k6: `https://k6.io/docs/get-started/installation/`
- Node.js and npm installed
- Worldmine application running locally (or update BASE_URL)

### Running Tests

1. **Basic Stress Test:**
```bash
k6 run k6-stress-test.js
```

2. **With Local Results:**
```bash
k6 run --out json=results.json k6-stress-test.js
```

3. **With LoadImpact Cloud:**
```bash
# Update project ID in the script
k6 run --out cloud k6-stress-test.js
```

## 📊 Test Scenarios

### Monday Morning Rush Scenario

The primary test simulates a typical Monday morning market activity pattern:

1. **Ramp-up (2 minutes):** 0 → 200 concurrent users
2. **Sustained Load (5 minutes):** 200 users browsing listings and news
3. **Market Alert Spike (1 minute):** 200 → 500 users (breaking news)
4. **Ramp-down (2 minutes):** 500 → 0 users

### User Personas

The test simulates realistic user behavior with 4 personas:

- **Casual Browse (40%):** Browse listings, check news
- **Active Trader (30%):** Browse listings, check prices, view details
- **News Reader (20%):** Check news, check prices
- **Power User (10%):** All actions including interactions

### Key Performance Indicators (KPIs)

- **P95 Latency:** < 800ms for ListingCard loading
- **Error Rate:** < 1%
- **Supabase Throughput:** Monitor Realtime connection stability
- **News Fetch:** < 600ms for Daily Mini news
- **Price Updates:** < 400ms for commodity prices

## 🎯 Thresholds

The test automatically fails if any of these thresholds are exceeded:

```javascript
thresholds: {
  http_req_duration: ['p(95)<800'],     // Overall response time
  http_req_failed: ['rate<0.01'],        // Error rate < 1%
  listing_card_latency: ['p(95)<800'],   // ListingCard loading
  news_fetch_latency: ['p(95)<600'],     // News API response
  supabase_latency: ['p(95)<400'],       // Database queries
  errors: ['rate<0.01'],                 // Custom error tracking
}
```

## 📈 Metrics Tracked

### Custom Metrics
- `listing_card_latency`: Time to load marketplace listings
- `news_fetch_latency`: Time to fetch market news
- `supabase_latency`: Database query response times
- `errors`: Custom error rate tracking

### Built-in Metrics
- `http_req_duration`: Overall HTTP request duration
- `http_req_failed`: HTTP request failure rate
- `vus`: Virtual users active
- `iteration_duration`: Complete iteration time

## 🔧 Configuration

### Environment Variables

Update these variables in the script:

```javascript
const BASE_URL = 'http://localhost:3000';           // Frontend URL
const API_BASE_URL = 'http://localhost:3000/api';   // API URL
```

### Test Data

The test uses sample data:
- Listing IDs: ['1', '2', '3', '4', '5']
- Search terms: ['gold', 'silver', 'copper', 'diamond', 'rare earth']
- News categories: ['Mini', 'Economic', 'Supply']

## 📊 Results Analysis

### Success Criteria

A test is considered successful if:
- ✅ P95 latency < 800ms
- ✅ Error rate < 1%
- ✅ No Supabase connection drops during spike
- ✅ All user personas complete successfully

### Common Issues

1. **High Latency:**
   - Check server resources
   - Verify database connections
   - Review CDN performance

2. **Connection Drops:**
   - Monitor Supabase Realtime limits
   - Check WebSocket connections
   - Verify network stability

3. **High Error Rate:**
   - Review application logs
   - Check API rate limits
   - Verify database capacity

## 🚨 Alerting

### LoadImpact Cloud Integration

Set up alerts in LoadImpact:
- Latency > 1s
- Error rate > 2%
- Connection failures
- Memory/CPU usage

### Local Monitoring

Monitor these metrics during testing:
```bash
# CPU and Memory
top -p $(pgrep node)

# Network Connections
netstat -an | grep :3000

# Application Logs
tail -f logs/application.log
```

## 📝 Test Reports

### Generating Reports

1. **HTML Report:**
```bash
k6 run --out html=report.html k6-stress-test.js
```

2. **JSON Report:**
```bash
k6 run --out json=results.json k6-stress-test.js
```

3. **InfluxDB:**
```bash
k6 run --out influxdb=http://localhost:8086 k6-stress-test.js
```

### Report Analysis

Key metrics to analyze:
- Response time percentiles (p50, p95, p99)
- Error rates by endpoint
- User journey completion rates
- Resource utilization patterns

## 🔍 Debugging

### Common Debugging Commands

```bash
# Verbose output
k6 run -v k6-stress-test.js

# Debug specific scenario
k6 run --vus 10 --duration 30s k6-stress-test.js

# Check syntax
k6 run --dry-run k6-stress-test.js
```

### Troubleshooting

1. **Connection Refused:**
   - Verify application is running
   - Check port configuration
   - Confirm firewall settings

2. **Authentication Issues:**
   - Verify API keys
   - Check token expiration
   - Review auth endpoints

3. **Database Errors:**
   - Check connection strings
   - Verify database limits
   - Review query performance

## 📚 Additional Tests

### Custom Scenarios

Create additional test files for:
- `api-only-test.js`: API endpoint testing
- `websocket-test.js`: Realtime connection testing
- `stress-test.js`: Maximum capacity testing

### CI/CD Integration

Add to your CI pipeline:
```yaml
performance_test:
  stage: test
  script:
    - npm start &
    - sleep 30
    - k6 run performance/k6-stress-test.js
    - kill %1
  artifacts:
    reports:
      junit: performance-results.xml
```

## 🆘 Support

For issues with:
- **k6:** https://k6.io/docs/
- **LoadImpact:** https://support.k6.io/
- **Worldmine:** Check application logs and monitoring

---

**Last Updated:** March 30, 2026  
**Version:** 1.0.0  
**Maintainer:** SRE Team
