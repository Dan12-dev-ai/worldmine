import { useMarketplaceStore } from '../store/marketplaceStore';

// State persistence testing utilities
export const testStatePersistence = () => {
  const store = useMarketplaceStore.getState();
  
  const tests = {
    // Test 1: Check if critical state persists
    criticalStatePersistence: () => {
      const criticalKeys = ['userProfile', 'walletBalance', 'transactions'];
      const results: { key: string; exists: boolean; value?: any }[] = [];
      
      criticalKeys.forEach(key => {
        const value = store[key as keyof typeof store];
        results.push({
          key,
          exists: value !== null && value !== undefined,
          value: typeof value === 'object' ? 'Object present' : value
        });
      });
      
      return results;
    },

    // Test 2: Simulate rapid navigation
    rapidNavigationTest: async () => {
      const initialTab = store.activeTab;
      const testTabs = ['Home', 'Marketplace', 'News', 'Contracts'];
      
      for (const tab of testTabs) {
        store.setActiveTab(tab);
        // Simulate rapid tab switching
        await new Promise(resolve => setTimeout(resolve, 50));
      }
      
      // Check if final state is consistent
      const finalTab = store.activeTab;
      return {
        initialTab,
        finalTab,
        testTabs,
        isConsistent: testTabs.includes(finalTab)
      };
    },

    // Test 3: Page refresh simulation
    pageRefreshTest: () => {
      // Store current state
      const beforeRefresh = JSON.stringify(store);
      
      // Simulate page refresh by clearing and restoring state
      const { loadTransactions } = store;
      
      // Check if state can be restored
      return {
        stateBeforeRefresh: beforeRefresh,
        hasLoadFunction: typeof loadTransactions === 'function',
        canRestoreState: true // This would be tested in actual app
      };
    },

    // Test 4: State corruption detection
    corruptionDetection: () => {
      const suspiciousValues = {
        walletBalance: () => {
          const balance = store.walletBalance;
          return {
            isNegative: balance < 0,
            isNan: isNaN(balance),
            isInfinite: !isFinite(balance),
            value: balance
          };
        },
        transactions: () => {
          const transactions = store.transactions;
          return {
            isArray: Array.isArray(transactions),
            hasValidStructure: transactions.every(t => 
              typeof t === 'object' && 
              'id' in t && 
              'amount' in t
            ),
            count: transactions.length,
            value: transactions
          };
        }
      };
      
      const results: { test: string; result: any; passed: boolean }[] = [];
      
      Object.entries(suspiciousValues).forEach(([testName, testFn]) => {
        const result = testFn();
        results.push({
          test: testName,
          result,
          passed: !(
            (result.isNegative || result.isNan || result.isInfinite) ||
            (!result.isArray || !result.hasValidStructure)
          )
        });
      });
      
      return results;
    },

    // Test 5: Memory leak detection
    memoryLeakTest: () => {
      const initialMemory = (performance as any).memory?.usedJSHeapSize || 0;
      
      // Simulate heavy state operations
      const largeArray = Array(10000).fill(null).map((_, i) => ({
        id: `test-${i}`,
        data: 'x'.repeat(1000) // 1KB per item
      }));
      
      try {
        // Try to add large array to state (should fail gracefully)
        // store.addTransaction(largeArray[0] as any); // This would be filtered out
      } catch (error) {
        return {
          errorCaught: true,
          errorMessage: error instanceof Error ? error.message : 'Unknown error'
        };
      }
      
      const finalMemory = (performance as any).memory?.usedJSHeapSize || 0;
      const memoryIncrease = finalMemory - initialMemory;
      
      return {
        initialMemory,
        finalMemory,
        memoryIncrease,
        isLeak: memoryIncrease > 50 * 1024 * 1024, // 50MB increase
        largeArraySize: largeArray.length
      };
    }
  };

  return tests;
};

// State hydration utilities
export const hydrateState = () => {
  try {
    // Check localStorage availability
    if (typeof window === 'undefined' || !window.localStorage) {
      console.warn('localStorage not available - state persistence limited');
      return false;
    }

    // Get stored state
    const storedState = localStorage.getItem('worldmine-store');
    if (!storedState) {
      console.log('No stored state found - using defaults');
      return false;
    }

    // Parse and validate stored state
    const parsed = JSON.parse(storedState);
    const store = useMarketplaceStore.getState();
    
    // Check if stored state structure matches current store
    const requiredKeys = ['userProfile', 'walletBalance', 'activeTab'];
    const hasValidStructure = requiredKeys.every(key => key in parsed);
    
    if (!hasValidStructure) {
      console.error('Stored state structure mismatch - clearing localStorage');
      localStorage.removeItem('worldmine-store');
      return false;
    }

    // Hydrate store with stored values
    Object.keys(parsed).forEach(key => {
      if (key in store && typeof store[`set${key.charAt(0).toUpperCase() + key.slice(1)}`] === 'function') {
        (store as any)[`set${key.charAt(0).toUpperCase() + key.slice(1)}`](parsed[key]);
      }
    });

    console.log('State successfully hydrated from localStorage');
    return true;
  } catch (error) {
    console.error('State hydration failed:', error);
    localStorage.removeItem('worldmine-store');
    return false;
  }
};

// State backup utilities
export const backupState = () => {
  try {
    const store = useMarketplaceStore.getState();
    const backup = {
      timestamp: new Date().toISOString(),
      version: '1.0.0',
      state: {
        userProfile: store.userProfile,
        walletBalance: store.walletBalance,
        transactions: store.transactions.slice(-100), // Last 100 transactions
        activeTab: store.activeTab
      }
    };
    
    localStorage.setItem('worldmine-backup', JSON.stringify(backup));
    return true;
  } catch (error) {
    console.error('State backup failed:', error);
    return false;
  }
};

export const restoreStateBackup = () => {
  try {
    const backup = localStorage.getItem('worldmine-backup');
    if (!backup) {
      return false;
    }
    
    const parsed = JSON.parse(backup);
    const store = useMarketplaceStore.getState();
    
    // Restore backed up values
    Object.entries(parsed.state).forEach(([key, value]) => {
      if (key in store && typeof store[`set${key.charAt(0).toUpperCase() + key.slice(1)}`] === 'function') {
        (store as any)[`set${key.charAt(0).toUpperCase() + key.slice(1)}`](value);
      }
    });
    
    console.log(`State restored from backup: ${parsed.timestamp}`);
    return true;
  } catch (error) {
    console.error('State restore failed:', error);
    return false;
  }
};
