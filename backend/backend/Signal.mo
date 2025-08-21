import Text "mo:base/Text";
import Nat "mo:base/Nat";
import Float "mo:base/Float";
import Time "mo:base/Time";
import TrieMap "mo:base/TrieMap";
import Principal "mo:base/Principal";
import Iter "mo:base/Iter";
import Types "../Types";

persistent actor {

  var signalIdCounter : Nat = 0;

  var stableSignals : [(Text, Types.Signal)] = [];
  private transient var signals = TrieMap.TrieMap<Text, Types.Signal>(Text.equal, Text.hash);

  system func preupgrade() {
    stableSignals := Iter.toArray(signals.entries());
  };

  system func postupgrade() {
    signals := TrieMap.fromEntries<Text, Types.Signal>(Iter.fromArray(stableSignals), Text.equal, Text.hash);
  };

  public func getUserSignals(principal : Principal) : async [(Text, Types.Signal)] {
    let key = Principal.toText(principal);
    switch (signals.get(key)) {
      case null return [];
      case (?signal) return [(key, signal)];
    };
  };

  public func getAllSignals() : async [(Text, Types.Signal)] {
    return Iter.toArray(signals.entries());
  };

  public func createSignal(
    user : Principal,
    signalMessage : Text,
    signalType : Text,
    confidenceScore : Float,
    generatedAt : Time.Time,
  ) : async Types.Signal {
    signalIdCounter += 1;

    let paddedNum = if (signalIdCounter < 10) {
      "00" # Nat.toText(signalIdCounter);
    } else if (signalIdCounter < 100) {
      "0" # Nat.toText(signalIdCounter);
    } else {
      Nat.toText(signalIdCounter);
    };

    let signalId : Text = "SGN-" # paddedNum;

    let newSignal : Types.Signal = {
      signalId = signalId;
      user = user;
      signalMessage = signalMessage;
      signalType = signalType;
      confidenceScore = confidenceScore;
      generatedAt = generatedAt;
    };
    signals.put(signalId, newSignal);

    return newSignal;
  };
};
