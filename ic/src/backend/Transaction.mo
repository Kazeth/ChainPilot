import Text "mo:base/Text";
import Nat "mo:base/Nat";
import Float "mo:base/Float";
import Time "mo:base/Time";
import TrieMap "mo:base/TrieMap";
import Principal "mo:base/Principal";
import Iter "mo:base/Iter";
import Types "../Types";

persistent actor {
  var transactionIdCounter : Nat = 0;

  var stableTransactions : [(Text, Types.Transaction)] = [];
  private transient var transactions = TrieMap.TrieMap<Text, Types.Transaction>(Text.equal, Text.hash);

  system func preupgrade() {
    stableTransactions := Iter.toArray(transactions.entries());
  };

  system func postupgrade() {
    transactions := TrieMap.fromEntries<Text, Types.Transaction>(Iter.fromArray(stableTransactions), Text.equal, Text.hash);
  };

  public query func getAllUserTransactions(principal : Principal) : async [(Text, Types.Transaction)] {
    Iter.toArray(
      Iter.filter<(Text, Types.Transaction)>(
        transactions.entries(),
        func((_, tx)) { tx.user == principal } 
      )
    );
  };

  public func getAllTransactions() : async [(Text, Types.Transaction)] {
    return Iter.toArray(transactions.entries());
  };

  public func createTransaction(
    user : Principal,
    fromAddress : Text,
    toAddress : Text,
    amount : Float,
    status : Types.TransactionStatus,
    network : Text,
    txType : Types.TransactionType,
    timestamp : Time.Time,
  ) : async Types.Transaction {
    transactionIdCounter += 1;

    let paddedNum = if (transactionIdCounter < 10) {
      "00" # Nat.toText(transactionIdCounter);
    } else if (transactionIdCounter < 100) {
      "0" # Nat.toText(transactionIdCounter);
    } else {
      Nat.toText(transactionIdCounter);
    };

    let transactionId : Text = "TSX-" # paddedNum;

    let newTransaction : Types.Transaction = {
      user = user;
      transactionId = transactionId;
      fromAddress = fromAddress;
      toAddress = toAddress;
      amount = amount;
      status = status;
      network = network;
      txType = txType;
      timestamp = timestamp;
    };
    transactions.put(transactionId, newTransaction);

    return newTransaction;
  };
};
