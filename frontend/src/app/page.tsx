export default function Home() {
  return (
    <main className="min-h-screen flex items-center justify-center bg-gradient-to-b from-gray-50 to-gray-100">
      <div className="text-center">
        <h1 className="text-4xl font-bold text-gray-900 mb-4">ContextMeet</h1>
        <p className="text-xl text-gray-600 mb-8">
          AI-Powered Meeting Context Assistant
        </p>
        <p className="text-gray-500 max-w-md">
          Application is initializing. Please wait...
        </p>
      </div>
    </main>
  );
}
