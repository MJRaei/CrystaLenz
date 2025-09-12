import Link from 'next/link';

export default function HomePage() {
  return (
    <main className="min-h-[80vh] grid place-items-center p-6">
      <div className="max-w-2xl text-center">
        <img src="/logo.jpg" alt="CrystaLens logo" className="mx-auto mb-6 h-48 w-48 rounded-full object-cover" />
        <h1 className="text-4xl font-semibold tracking-tight text-slate-900">CrystaLens</h1>
        <p className="mt-3 text-slate-600">Interactive console for your agentic system.</p>
        <div className="mt-6">
          <Link href="/console" className="inline-flex items-center rounded-lg bg-[#d6512f] px-5 py-3 text-white shadow hover:bg-[#c24728] active:bg-[#a83f25] transition">
            Go to console →
          </Link>
        </div>
      </div>
    </main>
  );
}
