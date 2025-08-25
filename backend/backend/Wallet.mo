import Text "mo:base/Text";
import Nat "mo:base/Nat";
import Float "mo:base/Float";
import TrieMap "mo:base/TrieMap";
import Principal "mo:base/Principal";
import Iter "mo:base/Iter";
import Array "mo:base/Array";
import Types "../Types";
import Error "mo:base/Error"; 
import MarketDataBackend "canister:marketData_backend";

persistent actor {

  var walletIdCounter : Nat = 0;
  var demoWalletIdCounter : Nat = 0;

  var stableWallets : [(Principal, [Types.Wallet])] = [];
  private transient var wallets = TrieMap.TrieMap<Principal, [Types.Wallet]>(Principal.equal, Principal.hash);

  var stableHoldings : [(Text, [Types.Holding])] = [];
  private transient var holdings = TrieMap.TrieMap<Text, [Types.Holding]>(Text.equal, Text.hash);

  system func preupgrade() {
    stableWallets := Iter.toArray(wallets.entries());
    stableHoldings := Iter.toArray(holdings.entries());
  };

  system func postupgrade() {
    wallets := TrieMap.fromEntries<Principal, [Types.Wallet]>(Iter.fromArray(stableWallets), Principal.equal, Principal.hash);
    holdings := TrieMap.fromEntries<Text, [Types.Holding]>(Iter.fromArray(stableHoldings), Text.equal, Text.hash);
  };

  public query func checkNewAddress(walletAddress : Text) : async Bool {
    let allWallets = Iter.toArray(wallets.entries());

    for ((_, walletArr) in allWallets.vals()) {
      for (w in walletArr.vals()) {
        if (w.walletAddress == walletAddress) {
          return false;
        };
      };
    };

    return true;
  };

  public query func checkWalletExistence(walletAddress : Text) : async Bool {
    let allWallets = Iter.toArray(wallets.entries());

    for ((_, walletArr) in allWallets.vals()) {
      for (w in walletArr.vals()) {
        if (w.walletAddress == walletAddress) {
          return true;
        };
      };
    };

    return false;
  };

  public query func getAllWallets() : async [(Principal, [Types.Wallet])] {
    return Iter.toArray(wallets.entries());
  };

  public query func getHoldingsByWalletId(walletId : Text) : async [(Text, [Types.Holding])] {
    switch (holdings.get(walletId)) {
      case (?holdingArr) { [(walletId, holdingArr)] };
      case null { [] };
    };
  };

  public query func getWalletsByPrincipal(principal : Principal) : async [Types.Wallet] {
    switch (wallets.get(principal)) {
      case (?walletArr) return walletArr;
      case null return [];
    };
  };

  public query func getWalletByWalletId(walletId : Text) : async Types.Wallet {
    let allWallets = Iter.toArray(wallets.entries());

    for ((_, walletArr) in allWallets.vals()) {
      for (w in walletArr.vals()) {
        if (w.walletId == walletId) {
          return w;
        };
      };
    };

    throw Error.reject("Wallet not found: " # walletId);
  };

  public func updateWallet(wallet : Types.Wallet) : async Bool {
    switch (wallets.get(wallet.owner)) {
      case (?arr) {
        let filtered = Array.filter<Types.Wallet>(
          arr,
          func(w : Types.Wallet) : Bool {
            w.walletId != wallet.walletId;
          },
        );
        let updated = Array.append(filtered, [wallet]);
        wallets.put(wallet.owner, updated);
        return true;
      };
      case null {
        return false;
      };
    };
  };

  public func updateWalletBalanceByWalletId(walletId : Text, newBalance : Float) : async Types.Wallet {
    let allWallets = Iter.toArray(wallets.entries());

    for ((principal, walletArr) in allWallets.vals()) {
      var found : ?Types.Wallet = null;
      let updatedArr = Array.map<Types.Wallet, Types.Wallet>(
        walletArr,
        func(w : Types.Wallet) : Types.Wallet {
          if (w.walletId == walletId) {
            let updatedWallet : Types.Wallet = {
              walletId = w.walletId;
              walletAddress = w.walletAddress;
              owner = w.owner;
              blockchainNetwork = w.blockchainNetwork;
              balance = newBalance;
              connectedExchange = w.connectedExchange;
            };
            found := ?updatedWallet;
            return updatedWallet;
          } else {
            return w;
          };
        },
      );

      wallets.put(principal, updatedArr);

      switch (found) {
        case (?uw) return uw;
        case null throw Error.reject("Wallet not found: " # walletId);
      };
    };

    throw Error.reject("Wallet not found: " # walletId);
  };

  public func clearWallet(walletId : Text) : async Bool {
    let allWallets = Iter.toArray(wallets.entries());

    for ((principal, walletArr) in allWallets.vals()) {
      var found : ?Types.Wallet = null;
      let updatedArr = Array.map<Types.Wallet, Types.Wallet>(
        walletArr,
        func(w : Types.Wallet) : Types.Wallet {
          if (w.walletId == walletId) {
            let updatedWallet : Types.Wallet = {
              walletId = w.walletId;
              walletAddress = w.walletAddress;
              owner = w.owner;
              blockchainNetwork = w.blockchainNetwork;
              balance = 0;
              connectedExchange = w.connectedExchange;
            };
            found := ?updatedWallet;
            return updatedWallet;
          } else {
            return w;
          };
        },
      );

      wallets.put(principal, updatedArr);

      ignore holdings.remove(walletId);

      return true;
    };

    return false;
  };

  // wallet's holding
  public func addHoldingToUserWallet(
    walletId : Text,
    assetId : Text,
    amount : Float,
    valueInUSD : Float,
  ) : async Types.Holding {

    let optAsset = await MarketDataBackend.getAssetByAssetId(assetId);

    switch (optAsset) {
      case (?asset) {
        let newHolding : Types.Holding = {
          asset = asset;
          amount = amount;
          valueUSD = valueInUSD;
        };

        let existingHoldings = switch (holdings.get(walletId)) {
          case (?arr) { arr };
          case null { [] };
        };

        let updatedHoldings = Array.append(existingHoldings, [newHolding]);
        holdings.put(walletId, updatedHoldings);

        return newHolding;
      };
      case null {
        throw Error.reject("Asset not found: " # assetId);
      };
    };

  };

  // demo wallet
  public func addDemoWallet(
    walletAddress : Text,
    owner : Principal,
    blockchainNetwork : Text,
    connectedExchange : Text,
  ) : async Types.Wallet {
    demoWalletIdCounter += 1;

    let paddedNum = if (demoWalletIdCounter < 10) {
      "00" # Nat.toText(demoWalletIdCounter);
    } else if (demoWalletIdCounter < 100) {
      "0" # Nat.toText(demoWalletIdCounter);
    } else {
      Nat.toText(demoWalletIdCounter);
    };

    let demoWalletId : Text = "D_WLT-" # paddedNum;
    let balance : Float = 10000;

    let newWallet : Types.Wallet = {
      walletId = demoWalletId;
      walletAddress = walletAddress;
      owner = owner;
      blockchainNetwork = blockchainNetwork;
      balance = balance;
      connectedExchange = connectedExchange;
    };

    let existingWallets = switch (wallets.get(owner)) {
      case (?arr) { arr };
      case (null) { [] };
    };

    let updatedWallets = Array.append(existingWallets, [newWallet]);
    wallets.put(owner, updatedWallets);

    return newWallet;
  };

  // custodial wallet
  public func addWallet(
    walletAddress : Text,
    owner : Principal,
    blockchainNetwork : Text,
    balance : Float,
    connectedExchange : Text,
  ) : async Types.Wallet {
    walletIdCounter += 1;

    let paddedNum = if (walletIdCounter < 10) {
      "00" # Nat.toText(walletIdCounter);
    } else if (walletIdCounter < 100) {
      "0" # Nat.toText(walletIdCounter);
    } else {
      Nat.toText(walletIdCounter);
    };

    let walletId : Text = "WLT-" # paddedNum;

    let newWallet : Types.Wallet = {
      walletId = walletId;
      walletAddress = walletAddress;
      owner = owner;
      blockchainNetwork = blockchainNetwork;
      balance = balance;
      connectedExchange = connectedExchange;
    };

    let existingWallets = switch (wallets.get(owner)) {
      case (?arr) { arr };
      case (null) { [] };
    };

    let updatedWallets = Array.append(existingWallets, [newWallet]);
    wallets.put(owner, updatedWallets);

    return newWallet;
  };
};
