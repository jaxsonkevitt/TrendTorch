import fs from 'fs';
import path from 'path';
import TrendingProducts from '@/components/TrendingProducts';

export default function Home() {
  const jsonDirectory = path.join(process.cwd(), 'json');
  const fileContents = fs.readFileSync(jsonDirectory + '/filtered_trends.json', 'utf8');
  const trends = JSON.parse(fileContents);

  return (
    <main style={{ padding: '32px 0', width: '100%', maxWidth: '1200px', margin: '0 auto' }}>
      <h1 style={{ fontSize: '2.5rem', fontWeight: 'bold', marginBottom: '16px', textAlign: 'center' }}>TrendTorch</h1>
      <p style={{ textAlign: 'center', marginBottom: '8px', color: '#666' }}>Google processes approximately 99,000 search queries every second, this translates to 8.5 billion searches per day and approximately 2 trillion global searches per year.</p>
      <p style={{ textAlign: 'center', marginBottom: '32px', color: '#666' }}>We scrape this data and use AI to find rising trends in products to help you gain a completive advantage.</p>
      <TrendingProducts trends={trends} />
    </main>
  );
}
