import http from 'k6/http';
import { check, sleep } from 'k6';
import { Rate, Trend } from 'k6/metrics';

// Custom metrics for monitoring
const errorRate = new Rate('errors');
const listingCardLatency = new Trend('listing_card_latency');
const newsFetchLatency = new Trend('news_fetch_latency');
const supabaseLatency = new Trend('supabase_latency');

// Test configuration
export const options = {
  stages: [
    { duration: '2m', target: 200 },  // Ramp-up to 200 users over 2 minutes
    { duration: '5m', target: 200 },  // Sustained load of 200 users for 5 minutes
    { duration: '1m', target: 500 },  // Spike to 500 users for 1 minute
    { duration: '2m', target: 0 },   // Ramp-down to 0 users
  ],
  thresholds: {
    http_req_duration: ['p(95)<800'], // 95th percentile under 800ms
    http_req_failed: ['rate<0.01'],    // Error rate below 1%
    listing_card_latency: ['p(95)<800'],
    news_fetch_latency: ['p(95)<600'],
    supabase_latency: ['p(95)<400'],
    errors: ['rate<0.01'],
  },
  ext: {
    loadimpact: {
      projectID: 8675309, // Replace with your LoadImpact project ID
      name: 'Worldmine Monday Morning Rush',
    },
  },
};

// Base URL for the application
const BASE_URL = 'http://localhost:3000'; // Update with your production URL
const API_BASE_URL = 'http://localhost:3000/api'; // Update with your API URL

// User personas for realistic behavior
const userPersonas = [
  { name: 'casual_browse', weight: 0.4, actions: ['browse_listings', 'check_news'] },
  { name: 'active_trader', weight: 0.3, actions: ['browse_listings', 'check_prices', 'view_details'] },
  { name: 'news_reader', weight: 0.2, actions: ['check_news', 'check_prices'] },
  { name: 'power_user', weight: 0.1, actions: ['browse_listings', 'check_news', 'check_prices', 'view_details', 'simulate_interaction'] },
];

// Select a user persona based on weights
function selectPersona() {
  const random = Math.random();
  let cumulative = 0;
  
  for (const persona of userPersonas) {
    cumulative += persona.weight;
    if (random <= cumulative) {
      return persona;
    }
  }
  return userPersonas[0];
}

// Think time to simulate human behavior
function thinkTime(min = 1, max = 3) {
  sleep(Math.random() * (max - min) + min);
}

// Main test function
export default function () {
  const persona = selectPersona();
  const startTime = new Date().toISOString();
  
  console.log(`User ${__VU} starting as ${persona.name} at ${startTime}`);
  
  // Initialize session
  const session = http.cookieJar();
  
  try {
    // Execute persona-specific actions
    for (const action of persona.actions) {
      executeAction(action, session);
      thinkTime(1, 4); // Random think time between actions
    }
    
    console.log(`User ${__VU} completed ${persona.name} scenario successfully`);
    
  } catch (error) {
    console.error(`User ${__VU} failed in ${persona.name} scenario:`, error);
    errorRate.add(1);
  }
}

// Action execution functions
function executeAction(action, session) {
  switch (action) {
    case 'browse_listings':
      browseListings(session);
      break;
    case 'check_news':
      checkNews(session);
      break;
    case 'check_prices':
      checkPrices(session);
      break;
    case 'view_details':
      viewListingDetails(session);
      break;
    case 'simulate_interaction':
      simulateUserInteraction(session);
      break;
    default:
      console.warn(`Unknown action: ${action}`);
  }
}

// Browse commodity listings
function browseListings(session) {
  const response = http.get(`${BASE_URL}/marketplace`, {
    headers: {
      'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
      'Accept-Language': 'en-US,en;q=0.5',
      'Accept-Encoding': 'gzip, deflate',
      'User-Agent': 'k6-performance-test',
    },
    session,
  });
  
  const success = check(response, {
    'listings status is 200': (r) => r.status === 200,
    'listings response time < 800ms': (r) => r.timings.duration < 800,
    'listings contains content': (r) => r.body.includes('ListingCard') || r.body.includes('commodity'),
  });
  
  listingCardLatency.add(response.timings.duration);
  errorRate.add(!success);
  
  if (!success) {
    console.error('Listings browse failed:', response.status, response.body.substring(0, 200));
  }
}

// Check market news (Daily Mini)
function checkNews(session) {
  const response = http.get(`${API_BASE_URL}/market-news?category=Mini&limit=10`, {
    headers: {
      'Accept': 'application/json',
      'Content-Type': 'application/json',
    },
    session,
  });
  
  const success = check(response, {
    'news status is 200': (r) => r.status === 200,
    'news response time < 600ms': (r) => r.timings.duration < 600,
    'news is JSON': (r) => {
      try {
        JSON.parse(r.body);
        return true;
      } catch {
        return false;
      }
    },
    'news has data': (r) => {
      try {
        const data = JSON.parse(r.body);
        return Array.isArray(data) && data.length >= 0;
      } catch {
        return false;
      }
    },
  });
  
  newsFetchLatency.add(response.timings.duration);
  errorRate.add(!success);
  
  if (!success) {
    console.error('News fetch failed:', response.status, response.body.substring(0, 200));
  }
}

// Check commodity prices
function checkPrices(session) {
  const response = http.get(`${API_BASE_URL}/commodities/prices`, {
    headers: {
      'Accept': 'application/json',
      'Content-Type': 'application/json',
    },
    session,
  });
  
  const success = check(response, {
    'prices status is 200': (r) => r.status === 200,
    'prices response time < 400ms': (r) => r.timings.duration < 400,
    'prices is JSON': (r) => {
      try {
        JSON.parse(r.body);
        return true;
      } catch {
        return false;
      }
    },
  });
  
  supabaseLatency.add(response.timings.duration);
  errorRate.add(!success);
  
  if (!success) {
    console.error('Prices fetch failed:', response.status, response.body.substring(0, 200));
  }
}

// View specific listing details
function viewListingDetails(session) {
  // Simulate clicking on a random listing
  const listingIds = ['1', '2', '3', '4', '5']; // Sample listing IDs
  const randomId = listingIds[Math.floor(Math.random() * listingIds.length)];
  
  const response = http.get(`${BASE_URL}/listing/${randomId}`, {
    headers: {
      'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
      'Referer': `${BASE_URL}/marketplace`,
    },
    session,
  });
  
  const success = check(response, {
    'listing details status is 200': (r) => r.status === 200,
    'listing details response time < 800ms': (r) => r.timings.duration < 800,
    'listing details has content': (r) => r.body.length > 1000,
  });
  
  listingCardLatency.add(response.timings.duration);
  errorRate.add(!success);
}

// Simulate user interaction (form submission, etc.)
function simulateUserInteraction(session) {
  // Simulate a search or filter action
  const searchTerms = ['gold', 'silver', 'copper', 'diamond', 'rare earth'];
  const randomTerm = searchTerms[Math.floor(Math.random() * searchTerms.length)];
  
  const response = http.get(`${BASE_URL}/search?q=${encodeURIComponent(randomTerm)}`, {
    headers: {
      'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
      'Referer': `${BASE_URL}/marketplace`,
    },
    session,
  });
  
  const success = check(response, {
    'search status is 200': (r) => r.status === 200 || r.status === 404, // 404 is acceptable for no results
    'search response time < 1000ms': (r) => r.timings.duration < 1000,
  });
  
  errorRate.add(!success);
}

// Handle setup and teardown
export function setup() {
  console.log('Starting Worldmine Monday Morning Rush Stress Test');
  console.log('Test Configuration:');
  console.log('- Ramp-up: 0 to 200 users over 2 minutes');
  console.log('- Sustained: 200 users for 5 minutes');
  console.log('- Spike: 500 users for 1 minute');
  console.log('- P95 Latency Target: <800ms');
  console.log('- Error Rate Target: <1%');
  
  return {
    startTime: new Date().toISOString(),
  };
}

export function teardown(data) {
  console.log('Worldmine Stress Test Completed');
  console.log(`Test started at: ${data.startTime}`);
  console.log(`Test ended at: ${new Date().toISOString()}`);
  
  // Print summary statistics
  console.log('\n=== Performance Summary ===');
  console.log(`Listing Card P95 Latency: ${listingCardLatency.get('p(95)')}ms`);
  console.log(`News Fetch P95 Latency: ${newsFetchLatency.get('p(95)')}ms`);
  console.log(`Supabase P95 Latency: ${supabaseLatency.get('p(95)')}ms`);
  console.log(`Overall Error Rate: ${(errorRate.rate * 100).toFixed(2)}%`);
}
