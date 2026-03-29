export interface Commodity {
  id: string
  name: string
  symbol: string
  price: number
  change: number
  image: string
  description: string
}

export const commodities: Commodity[] = [
  {
    id: 'copper',
    name: 'Copper',
    symbol: 'CU',
    price: 8450.50,
    change: 2.4,
    image: 'https://images.unsplash.com/photo-1578662996442-48f60103fc96?w=400&h=300&fit=crop',
    description: 'High-grade copper ore for industrial applications'
  },
  {
    id: 'aluminium',
    name: 'Aluminium',
    symbol: 'AL',
    price: 2240.75,
    change: 1.2,
    image: 'https://images.unsplash.com/photo-1581094794329-c8112a89af12?w=400&h=300&fit=crop',
    description: 'Premium aluminium for aerospace and construction'
  },
  {
    id: 'gold',
    name: 'Gold',
    symbol: 'AU',
    price: 62450.00,
    change: 3.8,
    image: 'https://images.unsplash.com/photo-1585059895524-72359e06133a?w=400&h=300&fit=crop',
    description: '24K pure gold bars and investment grade bullion'
  },
  {
    id: 'rare-earths',
    name: 'Rare Earths',
    symbol: 'RE',
    price: 125000.00,
    change: 5.2,
    image: 'https://images.unsplash.com/photo-1611224923853-80b023f02d71?w=400&h=300&fit=crop',
    description: 'Strategic rare earth elements for technology manufacturing'
  },
  {
    id: 'lithium',
    name: 'Lithium',
    symbol: 'LI',
    price: 15750.25,
    change: 4.1,
    image: 'https://images.unsplash.com/photo-1622634213745-9aae4a7129b6?w=400&h=300&fit=crop',
    description: 'Battery-grade lithium carbonate for EV industry'
  },
  {
    id: 'iron-ore',
    name: 'Iron Ore',
    symbol: 'FE',
    price: 125.50,
    change: -0.8,
    image: 'https://images.unsplash.com/photo-1590487817434-a35d1b7e7b85?w=400&h=300&fit=crop',
    description: 'High-grade iron ore for steel production'
  }
]

export interface Listing {
  id: string
  title: string
  commodity: string
  price: number
  quantity: number
  location: string
  seller: string
  verified: boolean
  bestMatch: boolean
  premium: boolean
  image: string
  description: string
  liveChange: number
}

export const listings: Listing[] = [
  {
    id: '1',
    title: 'Battery-Grade Lithium Carbonate',
    commodity: 'lithium',
    price: 15750.25,
    quantity: 5000,
    location: 'Chile',
    seller: 'LithiumCorp Ltd',
    verified: true,
    bestMatch: true,
    premium: false,
    image: 'https://images.unsplash.com/photo-1578662996442-48f60103fc96?w=600&h=400&fit=crop',
    description: 'Premium battery-grade lithium carbonate, 99.9% purity',
    liveChange: 2.3
  },
  {
    id: '2',
    title: 'Premium Gold Ore - High Purity',
    commodity: 'gold',
    price: 62450.00,
    quantity: 100,
    location: 'South Africa',
    seller: 'GoldMines Inc',
    verified: true,
    bestMatch: false,
    premium: true,
    image: 'https://images.unsplash.com/photo-1585059895524-72359e06133a?w=600&h=400&fit=crop',
    description: 'High-purity gold ore, direct from mine',
    liveChange: 3.8
  },
  {
    id: '3',
    title: 'Rare Earth Elements - Strategic Supply',
    commodity: 'rare-earths',
    price: 125000.00,
    quantity: 50,
    location: 'Australia',
    seller: 'RareEarth Mining',
    verified: true,
    bestMatch: true,
    premium: true,
    image: 'https://images.unsplash.com/photo-1611224923853-80b023f02d71?w=600&h=400&fit=crop',
    description: 'Strategic rare earth elements for tech manufacturing',
    liveChange: 5.2
  },
  {
    id: '4',
    title: 'Premium Iron Ore - Aligned w Aluminium',
    commodity: 'iron-ore',
    price: 125.50,
    quantity: 10000,
    location: 'Brazil',
    seller: 'IronOre Global',
    verified: false,
    bestMatch: false,
    premium: false,
    image: 'https://images.unsplash.com/photo-1590487817434-a35d1b7e7b85?w=600&h=400&fit=crop',
    description: 'High-grade iron ore perfect for steel production',
    liveChange: -0.8
  },
  {
    id: '5',
    title: 'Industrial Copper Cathodes',
    commodity: 'copper',
    price: 8450.50,
    quantity: 2000,
    location: 'Peru',
    seller: 'CopperMines SA',
    verified: true,
    bestMatch: true,
    premium: false,
    image: 'https://images.unsplash.com/photo-1581094794329-c8112a89af12?w=600&h=400&fit=crop',
    description: 'Grade A copper cathodes for electrical applications',
    liveChange: 2.4
  },
  {
    id: '6',
    title: 'Aerospace Grade Aluminium',
    commodity: 'aluminium',
    price: 2240.75,
    quantity: 8000,
    location: 'Canada',
    seller: 'Aluminium Corp',
    verified: true,
    bestMatch: false,
    premium: true,
    image: 'https://images.unsplash.com/photo-1585059895524-72359e06133a?w=600&h=400&fit=crop',
    description: 'Premium aluminium for aerospace and automotive',
    liveChange: 1.2
  }
]
