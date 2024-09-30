import { NextResponse } from 'next/server';

export const runtime = 'edge'; // or 'nodejs'

export function GET() {
  console.log('Trending products API route called');
  // Return an array of sample products for testing
  const sampleProducts = [
    { name: "Product 1", trendScore: 95, platform: "Google" },
    { name: "Product 2", trendScore: 88, platform: "Google" },
    { name: "Product 3", trendScore: 75, platform: "Google" },
  ];
  return NextResponse.json(sampleProducts);
}
