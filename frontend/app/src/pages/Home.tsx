import { Link } from 'react-router-dom';

export default function Home() {
  return (
    <div className="flex flex-col items-center justify-center p-8 bg-white rounded-lg shadow-md max-w-4xl mx-auto my-12">
      <h1 className="text-4xl font-bold text-gray-800 mb-4">
        Welcome to our URL Shortener
      </h1>
      <p className="text-lg text-gray-600 text-center mb-8">
        Tired of long, clunky links? Our service helps you create short,
        memorable URLs that are perfect for sharing on social media, in emails,
        or anywhere else you need a clean link. It's fast, free, and incredibly
        easy to use.
      </p>

      <div className="w-full">
        <h2 className="text-2xl font-semibold text-gray-700 mb-6 text-center">
          How It Works
        </h2>
        <div className="flex flex-col md:flex-row justify-center items-stretch gap-8 text-center">
          {/* Step 1 */}
          <div className="flex flex-col items-center text-center flex-1 min-w-[250px] max-w-sm">
            <div className="w-16 h-16 bg-blue-500 text-white flex items-center justify-center rounded-full text-2xl font-bold mb-3">
              1
            </div>
            <h3 className="text-xl font-medium text-gray-800 mb-2">
              Get Your Full URL
            </h3>
            <p className="text-gray-600">
              Copy the long URL you want to shorten, making sure it includes
              `http://` or `https://`.
            </p>
          </div>

          {/* Step 2 */}
          <div className="flex flex-col items-center text-center flex-1 min-w-[250px] max-w-sm">
            <div className="w-16 h-16 bg-blue-500 text-white flex items-center justify-center rounded-full text-2xl font-bold mb-3">
              2
            </div>
            <h3 className="text-xl font-medium text-gray-800 mb-2">
              Send It to the Processing Page
            </h3>
            <p className="text-gray-600">
              Paste the URL into our form and click the "Shorten" button. Our
              system will instantly create a new, short link for you.
            </p>
          </div>

          {/* Step 3 */}
          <div className="flex flex-col items-center text-center flex-1 min-w-[250px] max-w-sm">
            <div className="w-16 h-16 bg-blue-500 text-white flex items-center justify-center rounded-full text-2xl font-bold mb-3">
              3
            </div>
            <h3 className="text-xl font-medium text-gray-800 mb-2">
              Use and Share It
            </h3>
            <p className="text-gray-600">
              Copy your new short URL. You can now use it on social media, in
              presentations, or anywhere else you need a clean,
              professional-looking link.
            </p>
          </div>
        </div>
      </div>

      <div className="mt-12 text-center">
        <Link
          to="/URLLink"
          className="px-8 py-4 bg-blue-600 text-white font-semibold rounded-lg shadow-lg hover:bg-blue-700 transition-colors duration-200 text-lg"
        >
          Get Started - Shorten Your First URL
        </Link>
      </div>
    </div>
  );
}
