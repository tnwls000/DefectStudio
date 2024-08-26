import Header from '../components/home/Header';
import Main from '../components/home/Main';

const Home = () => {
  return (
    <div className="Home">
      <header className="Header">
        <Header />
      </header>
      <main>
        <Main />
      </main>
    </div>
  );
};

export default Home;
