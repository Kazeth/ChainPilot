import Text "mo:base/Text";
import Blob "mo:base/Blob";
import Nat "mo:base/Nat";
import Nat16 "mo:base/Nat16";
import Nat32 "mo:base/Nat32";
import Float "mo:base/Float";
import Time "mo:base/Time";

module {
  // ----- HTTP types -----
  public type HeaderField = (Text, Text);

  public type HttpRequest = {
    method : Text;
    url : Text;
    headers : [HeaderField];
    body : Blob;
    certificate_version : ?Nat16;
  };

  public type HttpResponse = {
    status_code : Nat16;
    headers : [HeaderField];
    body : Blob;
    streaming_strategy : ?Null;
    upgrade : ?Bool;
  };

  // ----- API response types -----
  public type WelcomeResponse = {
    message : Text;
  };

  public type BalanceResponse = {
    address : Text;
    balance : Float;
    unit : Text;
  };

  public type UtxoResponse = {
    txid : Text;
    vout : Nat;
    value : Nat;
    confirmations : Nat;
  };

  public type AddressResponse = {
    address : Text;
  };

  public type SendResponse = {
    success : Bool;
    destination : Text;
    amount : Nat;
    txId : Text;
  };

  public type TestDataResponse = {
    id : Nat;
    name : Text;
    value : Float;
    isTest : Bool;
  };

  public type DummyTestResponse = {
    status : Text;
    data : {
      message : Text;
      timestamp : Text;
      testData : TestDataResponse;
    };
  };

  // ----- Bitcoin API types -----
  public type GetBalanceRequest = {
    address : Text;
    network : { #mainnet; #testnet; #regtest };
    min_confirmations : ?Nat32;
  };

  //
  // User & Wallet
  public type User = {
    user : Principal; // principal sebagai identitas user
    username : Text;
    email : Text; // opsional
    walletAddress : Text;
    portfolio : [Holding]; // daftar asset user
  };

  public type Holding = {
    asset : Asset; // referensi ke Asset global
    amount : Float; // jumlah coin yang dimiliki user
    valueUSD : Float; // total nilai USD (amount * currentPrice)
  };

  public type Wallet = {
    walletId : Text;
    walletAddress : Text;
    owner : Principal;
    blockchainNetwork : Text; // contoh: Ethereum, ICP, Solana
    balance : Float;
    connectedExchange : Text;
  };

  // Asset & Market Data
  public type Asset = {
    assetId : Text;
    symbol : Text; // BTC, ETH, ICP
    name : Text;
    currentPrice : Float;
    marketCap : Float;
    volume24h : Float;
    network : Text;
  };

  public type Candle = {
    assetSymbol : Text;
    timestamp : Time.Time;
    open : Float;
    high : Float;
    low : Float;
    close : Float;
    volume : Float;
  };

  // Trade / Order
  public type OrderType = { #BUY; #SELL };

  public type TradeStatus = { #Pending; #Executed; #Cancelled };

  public type Trade = {
    tradeId : Text;
    user : Principal;
    asset : Asset;
    orderType : OrderType;
    amount : Float;
    price : Float;
    status : TradeStatus;
    timestamp : Time.Time;
  };

  public type TradeAction = {
    action : Text;
    price : Float;
  };

  public type AutoTrade = {
    autoTradeId : Text;
    user : Principal;
    asset : Asset;
    assetAmount : Float; 
    tradeActions : [TradeAction];
  };

  // Signal / Alert
  // SignalType = AutoTrade[BUY/SELL/TP/SL] / Signal[BUY/SELL/HOLD];

  public type Signal = {
    signalId : Text;
    user : Principal;
    signalMessage : Text;
    signalType : Text;
    confidenceScore : Float; // 0.0 - 1.0
    generatedAt : Time.Time;
  };

  // Transaction

  public type TransactionType = {
    #Transfer; // kirim antar wallet
    #Buy; // beli cryptocurrency
    #Sell; // jual cryptocurrency
  };
  public type TransactionStatus = { #Confirmed; #Pending; #Failed };

  public type Transaction = {
    transactionId : Text;
    user : Principal;
    fromAddress : Text;
    toAddress : Text;
    amount : Float;
    status : TransactionStatus;
    network : Text;
    txType : TransactionType;
    timestamp : Time.Time;
  };

  // Audit Log
  public type AuditLog = {
    logId : Text;
    user : Principal;
    action : Text;
    timestamp : Time.Time;
    details : Text;
  };

  // Insurance
  public type Insurance = {
    user : Principal;
    walletAddress : Text;
    backUpWalletAddress : Text;
    email : Text;
    dateStart : Time.Time; 
    interval : Time.Time;
    warnCount : Nat;
  }

};
