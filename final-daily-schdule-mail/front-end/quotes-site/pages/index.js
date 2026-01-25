import Head from "next/head";
import axios from "axios";
import { useEffect, useState } from "react";

export default function Home({ randomQuote, error }) {
  const [mounted, setMounted] = useState(false);
  const [status, setStatus] = useState('');
  useEffect(() => setMounted(true), []);

  if (error) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-gradient-to-br from-rose-500 via-purple-600 to-indigo-700 text-white">
        <p className="text-xl font-semibold backdrop-blur-sm bg-white/10 p-6 rounded-2xl">{error.message}</p>
      </div>
    );
  }

  const sendMessage = async (event) => {
    event.preventDefault();
    setStatus('sending');
    try {
      const res = await axios.post(
        "https://byclh6knwl.execute-api.ap-south-1.amazonaws.com/dev/mailer",
        {
          name: event.target.name.value,
          email: event.target.email.value,
          message: `${event.target.message.value}\n\n✨ Quote of the day: "${randomQuote?.quote}" — ${randomQuote?.author}`,
        }
      );
      console.log("Subscription response:", res.data);
      setStatus('success');
      setTimeout(() => setStatus(''), 3000);
      event.target.reset();
    } catch (error) {
      console.error("Error sending message:", error);
      setStatus('error');
      setTimeout(() => setStatus(''), 3000);
    }
  };

  return (
    <div className="min-h-screen flex flex-col relative overflow-hidden" style={{background: 'linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%)'}}>
      <style jsx>{`
        @keyframes float { 0%, 100% { transform: translateY(0px); } 50% { transform: translateY(-15px); } }
        @keyframes blob { 0%, 100% { transform: translate(0, 0) scale(1); } 33% { transform: translate(30px, -50px) scale(1.1); } 66% { transform: translate(-20px, 20px) scale(0.9); } }
        .animate-float { animation: float 5s ease-in-out infinite; }
        .animate-blob { animation: blob 7s ease-in-out infinite; }
      `}</style>
      
      <div className="absolute top-0 left-0 w-96 h-96 bg-purple-300 rounded-full mix-blend-multiply filter blur-3xl opacity-30 animate-blob"></div>
      <div className="absolute top-0 right-0 w-96 h-96 bg-yellow-300 rounded-full mix-blend-multiply filter blur-3xl opacity-30 animate-blob" style={{animationDelay: '2s'}}></div>
      <div className="absolute bottom-0 left-1/2 w-96 h-96 bg-pink-300 rounded-full mix-blend-multiply filter blur-3xl opacity-30 animate-blob" style={{animationDelay: '4s'}}></div>

      <Head>
        <title>Inspirational Quotes</title>
        <link rel="icon" href="/favicon.ico" />
      </Head>

      <header className="relative bg-white bg-opacity-20 backdrop-blur-lg text-white py-6 shadow-lg border-b border-white border-opacity-30">
        <h1 className="relative text-4xl font-bold text-center bg-gradient-to-r from-yellow-600 via-pink-600 to-purple-600 bg-clip-text text-transparent">✨ Daily Inspiration ✨</h1>
      </header>

      <main className="relative flex-grow flex flex-col items-center justify-center px-4 py-8 text-center">
        {status && (
          <div className={`fixed top-20 right-4 px-6 py-3 rounded-lg shadow-2xl backdrop-blur-lg border-2 font-semibold animate-float z-50 ${
            status === 'success' ? 'bg-green-500 border-green-300 text-white' :
            status === 'error' ? 'bg-red-500 border-red-300 text-white' :
            'bg-blue-500 border-blue-300 text-white'
          }`}>
            {status === 'success' ? '✅ Subscribed Successfully!' :
             status === 'error' ? '❌ Subscription Failed!' :
             '⏳ Sending...'}
          </div>
        )}
        <h2 className="text-2xl font-bold text-white mb-6">
          Subscribe and Receive Inspirational Quotes Daily
        </h2>

        <div className={`relative bg-white bg-opacity-90 backdrop-blur-xl shadow-2xl rounded-2xl p-8 mb-8 max-w-md w-full border border-white border-opacity-40 ${mounted ? 'animate-float' : ''}`}>
          <p className="relative text-xl font-semibold text-gray-800 leading-relaxed">
            "{randomQuote?.quote || "No quote available"}"
          </p>
          <blockquote className="relative mt-4 text-base italic font-medium text-purple-700">
            — {randomQuote?.author || "Unknown"}
          </blockquote>
        </div>

        <form
          onSubmit={sendMessage}
          className="relative bg-white bg-opacity-90 backdrop-blur-xl shadow-2xl rounded-2xl p-6 max-w-md w-full space-y-4 border border-white border-opacity-40"
        >
          <div>
            <label htmlFor="name" className="block text-sm font-semibold text-gray-700 mb-1 text-left">
              Name
            </label>
            <input
              id="name"
              name="name"
              type="text"
              required
              className="w-full px-4 py-2 border-2 border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-purple-500 outline-none transition"
            />
          </div>

          <div>
            <label htmlFor="email" className="block text-sm font-semibold text-gray-700 mb-1 text-left">
              Email
            </label>
            <input
              id="email"
              name="email"
              type="email"
              required
              className="w-full px-4 py-2 border-2 border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-purple-500 outline-none transition"
            />
          </div>

          <div>
            <label htmlFor="message" className="block text-sm font-semibold text-gray-700 mb-1 text-left">
              Message
            </label>
            <textarea
              id="message"
              name="message"
              rows="3"
              required
              className="w-full px-4 py-2 border-2 border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-purple-500 outline-none transition resize-none"
            ></textarea>
          </div>

          <button
            type="submit"
            style={{background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'}}
            className="w-full py-3 text-white font-bold text-base rounded-lg shadow-lg hover:shadow-xl transition transform hover:scale-105 active:scale-95"
          >
            ✨ Subscribe Now ✨
          </button>
        </form>
      </main>

      <footer className="relative bg-white bg-opacity-20 backdrop-blur-lg text-white py-4 text-center border-t border-white border-opacity-30">
        <p className="relative text-sm font-medium">Powered by Awesomeness ✨ | Made with 💜</p>
      </footer>
    </div>
  );
}

export async function getServerSideProps() {
  try {
    const res = await axios.get(
      "https://byclh6knwl.execute-api.ap-south-1.amazonaws.com/dev/quotes"
    );
    const quotes = res.data;

    if (!quotes || !Array.isArray(quotes.quotes) || quotes.quotes.length === 0) {
      return {
        props: { randomQuote: { quote: "No quotes available", author: "System" } },
      };
    }

    const listLength = quotes.quotes.length;
    const randomQuote = quotes.quotes[Math.floor(Math.random() * listLength)];

    return { props: { randomQuote } };
  } catch (error) {
    return { props: { error: { message: error.message } } };
  }
}
