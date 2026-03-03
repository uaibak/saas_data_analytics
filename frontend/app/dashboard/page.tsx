const cards = [
  { title: "Total Datasets", value: "0" },
  { title: "Total Experiments", value: "0" },
  { title: "Recent Activity", value: "No activity yet" },
];

export default function DashboardPage() {
  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-semibold text-slate-900">Welcome back</h2>
        <p className="mt-1 text-sm text-slate-500">Your workspace overview is ready.</p>
      </div>
      <section className="grid gap-4 md:grid-cols-3">
        {cards.map((card) => (
          <article key={card.title} className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
            <h3 className="text-sm font-medium text-slate-500">{card.title}</h3>
            <p className="mt-2 text-xl font-semibold text-slate-900">{card.value}</p>
          </article>
        ))}
      </section>
    </div>
  );
}
