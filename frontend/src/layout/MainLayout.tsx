
import Header from '../components/Header';
import NewsletterCTA from '../components/NewsletterCTA';
import Footer from '../components/Footer';
import { Outlet, useLocation } from 'react-router-dom';


const MainLayout = () => {
  const location = useLocation();
  const isAnalyticsPage = location.pathname === '/analytics';
  
  return (
    <div className={`bg-zinc-900 text-white ${isAnalyticsPage ? 'h-screen' : 'min-h-screen'} w-screen flex flex-col`}>
      {/* The isLoggedIn prop has been removed from the Header */}
      <Header />

      {/* The main content of the page will be rendered here */}
      <main className={`flex-grow ${isAnalyticsPage ? 'overflow-hidden pt-20' : 'overflow-hidden pt-20'}`}>
        <Outlet />
      </main>

      {/* Newsletter and Footer - only show on non-analytics pages */}
      {!isAnalyticsPage && (
        <div className="py-16">
          <NewsletterCTA />
          <Footer />  
        </div>
      )}
      
  </div>
  );
};

export default MainLayout;
