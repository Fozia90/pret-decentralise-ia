import { useState } from "react";
import "./App.css";
import { CONTRACT_ADDRESS, CONTRACT_ABI } from "./contract";
import { BrowserProvider, Contract } from "ethers";

function App() {
  const [activePage, setActivePage] = useState("dashboard");
  const [account, setAccount] = useState("");
  const [networkName, setNetworkName] = useState("Non détecté");
  const [amount, setAmount] = useState("");
  const [score, setScore] = useState(null);
  const [contractRate, setContractRate] = useState(null);
  const [duration, setDuration] = useState("30");
  const [request, setRequest] = useState(null);
  const [history, setHistory] = useState(() => {
  const savedHistory = localStorage.getItem("creditHistory");
  return savedHistory ? JSON.parse(savedHistory) : [];
});
const totalRequests = history.length;

const totalAmount = history.reduce(
  (total, item) => total + Number(item.amount),
  0
);

const pendingRequests = history.filter(
  (item) => item.status === "En attente d'analyse"
).length;

  
  

  async function connectWallet() {
    if (!window.ethereum) {
      alert("Veuillez installer MetaMask.");
      return;
    }
function copyAddress() {
  if (!account) {
    alert("Veuillez d'abord connecter MetaMask.");
    return;
  }

  navigator.clipboard.writeText(account)
    .then(() => {
      alert("Adresse copiée avec succès !");
    })
    .catch(() => {
      alert("Impossible de copier l'adresse.");
    });
}
    try {
      const accounts = await window.ethereum.request({
        method: "eth_requestAccounts",
      });

      setAccount(accounts[0]);
      const provider = new BrowserProvider(window.ethereum);
const network = await provider.getNetwork();

if (network.chainId === 11155111n) {
  setNetworkName("Ethereum Sepolia");
} else {
  setNetworkName(network.name);
}
    } catch (error) {
      alert("Connexion au portefeuille annulée.");
    }
  }

  
    async function testContract() {
  try {
    const provider = new BrowserProvider(window.ethereum);
    const network = await provider.getNetwork();

    if (network.chainId !== 11155111n) {
      alert("Veuillez sélectionner le réseau Sepolia.");
      return;
    }

    const contract = new Contract(
      CONTRACT_ADDRESS,
      CONTRACT_ABI,
      provider
    );

    const rate = await contract.getInterestRate(85);
    setContractRate(Number(rate));

    alert("Connexion réussie ! Taux d'intérêt : " + rate + "%");

  } catch (error) {
    console.error(error);
    alert("Erreur de connexion au contrat. Vérifiez la console.");
  }
}
   function calculateRate(value) {
  if (value >= 80) return 5;
  if (value >= 60) return 10;
  if (value >= 40) return 15;
  return 20;
}
  async function simulateScore() {
  if (!amount || Number(amount) <= 0) {
    alert("Veuillez saisir un montant valide.");
    return;
  }

  try {
    const provider = new BrowserProvider(window.ethereum);
    const network = await provider.getNetwork();

    if (network.chainId !== 11155111n) {
      alert("Veuillez sélectionner le réseau Sepolia.");
      return;
    }

    const contract = new Contract(
      CONTRACT_ADDRESS,
      CONTRACT_ABI,
      provider
    );

    const demoScore = 85;
    const rate = await contract.getInterestRate(demoScore);

    setScore(demoScore);
    setContractRate(Number(rate));

  } catch (error) {
    console.error(error);
    alert("Impossible de récupérer le taux depuis le contrat.");
  }
}
  const rate = score === null ? null : calculateRate(score);

  return (
    <div className="app">
     <header className="header">

  {/* LOGO */}
  <div className="brand">
    <div className="logo">C</div>
    <div>
      <h2>CreditScore</h2>
      <p>Decentralized Lending</p>
    </div>
  </div>

  {/* NAVIGATION */}
  <nav className="navigation">

    <button
      className={activePage === "dashboard" ? "active" : ""}
      onClick={() => setActivePage("dashboard")}
    >
      Tableau de bord
    </button>

    <button
      className={activePage === "loan" ? "active" : ""}
      onClick={() => setActivePage("loan")}
    >
      Demander un prêt
    </button>

    <button
      className={activePage === "history" ? "active" : ""}
      onClick={() => setActivePage("history")}
    >
      Historique
    </button>

    <button
      className={activePage === "profile" ? "active" : ""}
      onClick={() => setActivePage("profile")}
    >
      Mon profil
    </button>

  </nav>

  {/* CONNEXION METAMASK */}
  <button className="wallet-button" onClick={connectWallet}>
    {account
      ? `${account.slice(0, 6)}...${account.slice(-4)}`
      : "Connecter MetaMask"}
  </button>

</header>

      <main className="main">
       {activePage === "dashboard" && (
  <section className="hero">
    <span className="badge">ESPACE EMPRUNTEUR</span>
    

    <h1>
      Bienvenue sur
      <br />
      <span>CreditScore.</span>
    </h1>

    <p>
      Gérez vos demandes de prêt et consultez
      vos informations de crédit en toute simplicité.
    </p>

    <button
      className="primary-button"
      onClick={() => setActivePage("loan")}
    >
      Demander un prêt
    </button>

   <div className="dashboard-stats">
      <div className="stat-card">
        <p>Total des demandes</p>
        <h2>{totalRequests}</h2>
      </div>

      <div className="stat-card">
        <p>Montant total demandé</p>
        <h2>{totalAmount} ETH</h2>
      </div>

      <div className="stat-card">
        <p>Demandes en attente</p>
        <h2>{pendingRequests}</h2>
      </div>
    </div>
  </section>
)}


{activePage === "loan" && (
  <section className="loan-card">
    <div className="card-heading">
      <div>
        <h2>Demander un prêt</h2>
        <p>Préparez votre demande de crédit.</p>
      </div>
      <span className="card-icon">↗</span>
    </div>

    <label>Montant souhaité (ETH)</label>
    <div className="input-wrapper">
      <input
  type="number"
  min="0.01"
  step="0.01"
  placeholder="Ex. 1"
  value={amount}
  onChange={(event) => setAmount(event.target.value)}
/>
      <span>ETH</span>
    </div>

    <label>Durée du prêt</label>

<select
  className="loan-select"
  value={duration}
  onChange={(event) => setDuration(event.target.value)}
>
  <option value="30">30 jours</option>
  <option value="60">60 jours</option>
  <option value="90">90 jours</option>
</select>
    <button
  className="primary-button"
  onClick={() => {
    if (!amount || Number(amount) <= 0) {
      alert("Veuillez saisir un montant valide.");
      return;
    }

    const newRequest = {
  amount: amount,
  duration: duration,
  status: "En attente d'analyse",
  date: new Date().toLocaleDateString("fr-FR"),
};

setRequest(newRequest);
setHistory((previousHistory) => [
  newRequest,
  ...previousHistory,
]);
localStorage.setItem(
  "creditHistory",
  JSON.stringify([newRequest, ...history])
);
  }}
>
  Analyser ma demande
</button>
    <button className="primary-button" onClick={testContract}>
  Tester le contrat intelligent
</button>
{request !== null && (
  <div className="result">
    
    <h3>Récapitulatif de votre demande</h3>
    <p>Montant : {request.amount} ETH</p>
    <p>Durée : {request.duration} jours</p>
    <small>
      Le score IA et l'enregistrement sur la blockchain
      ne sont pas encore connectés.
    </small>
  </div>
)}

{contractRate !== null && (
  <div className="result">
    <p>Taux récupéré depuis la blockchain</p>
    <h3>{contractRate}%</h3>
  </div>
)}

    <p className="notice">
      Les conditions seront déterminées après l'analyse de votre profil.
    </p>
  </section>
)}
{activePage === "history" && (
  <section className="loan-card">
    <div className="card-heading">
      <div>
        <h2>Historique des demandes</h2>
        <p>Retrouvez toutes vos demandes de prêt.</p>
      </div>
      <span className="card-icon">📋</span>
    </div>

    {history.length === 0 ? (
      <div className="result">
        <h3>Aucune demande pour le moment</h3>
        <p>
          Vos demandes de prêt apparaîtront ici
          après leur soumission.
        </p>

        <button
          className="primary-button"
          onClick={() => setActivePage("loan")}
        >
          Faire une demande
        </button>
      </div>
    ) : (
      <div>
        {history.map((item, index) => (
          <div className="result" key={index}>
            <h3>Demande #{index + 1}</h3>
            <p>Montant : {item.amount} ETH</p>
            <p>Durée : {item.duration} jours</p>
            <p>Statut : {item.status}</p>
            <p>Date : {item.date}</p>
          </div>
        ))}
      </div>
    )}
  </section>
)}
{activePage === "profile" && (
  <section className="loan-card">
    <div className="card-heading">
      <div>
        <h2>Mon profil</h2>
        <p>Informations de votre portefeuille.</p>
      </div>
      <span className="card-icon">👤</span>
    </div>

    <div className="result">
  <p>Adresse du portefeuille MetaMask</p>

  <p>
    {account
      ? account
      : "Aucun portefeuille connecté"}
  </p>
  

<p>Réseau blockchain</p>
<h3>{networkName}</h3>

  <p>État de connexion</p>
  <h3 className={account ? "connected-status" : "disconnected-status"}>
    {account ? "Connecté" : "Non connecté"}
  </h3>
</div>

    {!account && (
      <button
        className="primary-button"
        onClick={connectWallet}
      >
        Connecter MetaMask
      </button>
    )}
    <div className="dashboard-stats profile-stats">
  <div className="stat-card">
    <p>Total des demandes</p>
    <h2>{totalRequests}</h2>
  </div>

  <div className="stat-card">
    <p>Montant total demandé</p>
    <h2>{totalAmount} ETH</h2>
  </div>
</div>

    <div className="notice">
      <span>ⓘ</span>
      <p>
        Votre adresse de portefeuille permet de vous
        identifier dans cette démonstration.
      </p>
    </div>
  </section>
)}

      </main>

      <footer>
        CreditScore DApp 
      </footer>
    </div>
  );
}

export default App;