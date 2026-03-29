export interface Transaction {
  id: string
  listingTitle: string
  amount: number
  date: string
  status: 'Completed' | 'Pending' | 'Escrow'
  commission: number
}

const DB_NAME = 'DedanMarketplaceDB'
const STORE_NAME = 'transactions'
const DB_VERSION = 1

export const initDB = (): Promise<IDBDatabase> => {
  return new Promise((resolve, reject) => {
    const request = indexedDB.open(DB_NAME, DB_VERSION)

    request.onupgradeneeded = (event) => {
      const db = (event.target as IDBOpenDBRequest).result
      if (!db.objectStoreNames.contains(STORE_NAME)) {
        db.createObjectStore(STORE_NAME, { keyPath: 'id' })
      }
    }

    request.onsuccess = () => resolve(request.result)
    request.onerror = () => reject(request.error)
  })
}

export const saveTransaction = async (transaction: Transaction): Promise<void> => {
  const db = await initDB()
  return new Promise((resolve, reject) => {
    const transaction_store = db.transaction([STORE_NAME], 'readwrite')
    const store = transaction_store.objectStore(STORE_NAME)
    const request = store.add(transaction)

    request.onsuccess = () => resolve()
    request.onerror = () => reject(request.error)
  })
}

export const getAllTransactions = async (): Promise<Transaction[]> => {
  const db = await initDB()
  return new Promise((resolve, reject) => {
    const transaction_store = db.transaction([STORE_NAME], 'readonly')
    const store = transaction_store.objectStore(STORE_NAME)
    const request = store.getAll()

    request.onsuccess = () => resolve(request.result)
    request.onerror = () => reject(request.error)
  })
}
