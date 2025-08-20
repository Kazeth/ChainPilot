import Text "mo:base/Text";
import Nat "mo:base/Nat";
import Float "mo:base/Float";
import Time "mo:base/Time";
import TrieMap "mo:base/TrieMap";
import Principal "mo:base/Principal";
import Iter "mo:base/Iter";
import Array "mo:base/Array";
import Types "../Types";

persistent actor {

  var tradeIdCounter : Nat = 0;

  var stableTrades : [(Principal, [Types.Trade])] = [];
  private transient var trades = TrieMap.TrieMap<Principal, [Types.Trade]>(Principal.equal, Principal.hash);

  system func preupgrade() {
    stableTrades := Iter.toArray(trades.entries());
  };

  system func postupgrade() {
    trades := TrieMap.fromEntries<Principal, [Types.Trade]>(Iter.fromArray(stableTrades), Principal.equal, Principal.hash);
  };

  public query func getTradesByPrincipal(principal : Principal) : async [Types.Trade] {
    switch (trades.get(principal)) {
      case null return [];
      case (?logs) return Iter.toArray(logs.vals());
    };
  };

  public query func getAllTrades() : async [(Principal, [Types.Trade])] {
    Iter.toArray(trades.entries());
  };

  public func createTrade(
    user : Principal,
    assetSymbol : Text,
    orderType : Types.OrderType,
    amount : Float,
    price : Float,
    status : Types.TradeStatus,
    timestamp : Time.Time,
  ) : async Types.Trade {
    tradeIdCounter += 1;

    let paddedNum = if (tradeIdCounter < 10) {
      "00" # Nat.toText(tradeIdCounter);
    } else if (tradeIdCounter < 100) {
      "0" # Nat.toText(tradeIdCounter);
    } else {
      Nat.toText(tradeIdCounter);
    };

    let tradeId : Text = "TRD-" # paddedNum;

    let newTrade : Types.Trade = {
      tradeId = tradeId;
      user = user;
      assetSymbol = assetSymbol;
      orderType = orderType;
      amount = amount;
      price = price;
      status = status;
      timestamp = timestamp;
    };

    let existingTrades = switch (trades.get(user)) {
      case (?arr) { arr };
      case (null) { [] };
    };

    let updatedTrades = Array.append(existingTrades, [newTrade]);

    trades.put(user, updatedTrades);

    return newTrade;
  }

};
