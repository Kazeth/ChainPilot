import Text "mo:base/Text";
import Nat "mo:base/Nat";
import Float "mo:base/Float";
import TrieMap "mo:base/TrieMap";
import Iter "mo:base/Iter";
import Time "mo:base/Time";
import Array "mo:base/Array";
import Types "../Types";

persistent actor {

  var assetIdCounter : Nat = 0;

  var stableAssets : [(Text, Types.Asset)] = [];
  private transient var assets = TrieMap.TrieMap<Text, Types.Asset>(Text.equal, Text.hash);

  var stableCandles : [(Text, [Types.Candle])] = [];
  private transient var candles = TrieMap.TrieMap<Text, [Types.Candle]>(Text.equal, Text.hash);

  system func preupgrade() {
    stableAssets := Iter.toArray(assets.entries());
    stableCandles := Iter.toArray(candles.entries());
  };

  system func postupgrade() {
    assets := TrieMap.fromEntries<Text, Types.Asset>(Iter.fromArray(stableAssets), Text.equal, Text.hash);
    candles := TrieMap.fromEntries<Text, [Types.Candle]>(Iter.fromArray(stableCandles), Text.equal, Text.hash);
  };

  public query func getAssetCandlesByAssetId(assetId : Text) : async [Types.Candle] {
    switch (candles.get(assetId)) {
      case (?candleArr) { candleArr };
      case null { [] };
    };
  };

  public query func getAssetByAssetId(assetId : Text) : async ?Types.Asset {
    return assets.get(assetId);
  };

    public query func getAllAssets() : async [(Text, Types.Asset)] {
    return Iter.toArray(assets.entries());
  };

  public func addCandle(
    assetId : Text,
    assetSymbol : Text,
    timestamp : Time.Time,
    open : Float,
    high : Float,
    low : Float,
    close : Float,
    volume : Float,
  ) : async Types.Candle {
    let newCandle : Types.Candle = {
      assetSymbol = assetSymbol;
      timestamp = timestamp;
      open = open;
      high = high;
      low = low;
      close = close;
      volume = volume;
    };

    let existingCandles = switch (candles.get(assetId)) {
      case (?arr) { arr };
      case (null) { [] };
    };

    let updatedCandles = Array.append(existingCandles, [newCandle]);
    candles.put(assetId, updatedCandles);

    return newCandle;
  };

  public func addAsset(
    symbol : Text,
    name : Text,
    currentPrice : Float,
    marketCap : Float,
    volume24h : Float,
    network : Text,
  ) : async Types.Asset {
    assetIdCounter += 1;

    let paddedNum = if (assetIdCounter < 10) {
      "00" # Nat.toText(assetIdCounter);
    } else if (assetIdCounter < 100) {
      "0" # Nat.toText(assetIdCounter);
    } else {
      Nat.toText(assetIdCounter);
    };

    let assetId : Text = "AST-" # paddedNum;

    let newAsset : Types.Asset = {
      assetId = assetId;
      symbol = symbol;
      name = name;
      currentPrice = currentPrice;
      marketCap = marketCap;
      volume24h = volume24h;
      network = network;
    };
    assets.put(assetId, newAsset);

    return newAsset;
  };
};
