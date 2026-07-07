export default function HomePage() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center gap-4 p-8">
      <h1 className="text-4xl font-bold">InterviewerAI</h1>
      <p className="text-lg text-gray-600">
        Foundation ready. Interview features arrive in upcoming iterations.
      </p>
      <a
        href="/resumes"
        className="rounded-lg bg-indigo-600 px-5 py-2.5 font-medium text-white hover:bg-indigo-700"
      >
        Upload &amp; parse resume
      </a>
    </main>
  );
}
