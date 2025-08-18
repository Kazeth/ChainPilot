import React from 'react';
import Header from '../components/Header';
import NewsletterCTA from '../components/NewsletterCTA';
import Footer from '../components/Footer';

// Define the props to accept 'children', which will be the page-specific content.
interface MainLayoutProps {
  children: React.ReactNode;
}

const MainLayout: React.FC<MainLayoutProps> = ({ children }) => {
  return (
    <div className="bg-zinc-900 text-white min-h-screen flex flex-col">
      {/* The isLoggedIn prop has been removed from the Header */}
      <Header />

      {/* The main content of the page will be rendered here */}
      <main className="flex-grow pt-20">
        {children}
      </main>

      {/* Newsletter and Footer are consistently placed below the content */}
      <div className="container mx-auto px-4 sm:px-6 lg:px-8 py-16">
        <NewsletterCTA />
      </div>
      
      <Footer />
    </div>
  );
};

export default MainLayout;
