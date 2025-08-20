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

  public query func getHoldingsByWalletId(walletId : Text) : async [(Text, [Types.Holding])] {
    switch (holdings.get(walletId)) {
      case (?holdingArr) { [(walletId, holdingArr)] };
      case null { [] };
    };
  };

  public query func getWalletsByPrincipal(principal : Principal) : async [(Principal, [Types.Wallet])] {
    let mapped = Iter.map<(Principal, [Types.Wallet]), (Principal, [Types.Wallet])>(
      wallets.entries(),
      func((userPrincipal, walletArr)) {
        let userWallets = Iter.toArray(
          Iter.filter<Types.Wallet>(
            walletArr.vals(),
            func(t) { t.owner == principal },
          )
        );
        (userPrincipal, userWallets);
      },
    );
    Iter.toArray(mapped);
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

  // custodial wallet
  public func addWallet(
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
