import Text "mo:base/Text";
import Nat "mo:base/Nat";
import Time "mo:base/Time";
import TrieMap "mo:base/TrieMap";
import Principal "mo:base/Principal";
import Iter "mo:base/Iter";
import Array "mo:base/Array";
import Types "../Types";

persistent actor {

  var logIdCounter : Nat = 0;

  var stableAuditLogs : [(Principal, [Types.AuditLog])] = [];
  private transient var auditLogs = TrieMap.TrieMap<Principal, [Types.AuditLog]>(Principal.equal, Principal.hash);

  system func preupgrade() {
    stableAuditLogs := Iter.toArray(auditLogs.entries());
  };

  system func postupgrade() {
    auditLogs := TrieMap.fromEntries<Principal, [Types.AuditLog]>(Iter.fromArray(stableAuditLogs), Principal.equal, Principal.hash);
  };

  public query func getAllLogs() : async [(Principal, [Types.AuditLog])] {
    return Iter.toArray(auditLogs.entries());
  };

  public query func getLogsByPrincipal(principal : Principal) : async [Types.AuditLog] {
    switch (auditLogs.get(principal)) {
      case null return [];
      case (?logs) return Iter.toArray(logs.vals());
    };
  };

  public func createLog(
    userPrincipal : Principal,
    action : Text,
    timestamp : Time.Time,
    details : Text,
  ) : async Types.AuditLog {
    logIdCounter += 1;

    let paddedNum = if (logIdCounter < 10) {
      "00" # Nat.toText(logIdCounter);
    } else if (logIdCounter < 100) {
      "0" # Nat.toText(logIdCounter);
    } else {
      Nat.toText(logIdCounter);
    };

    let logId : Text = "LOG-" # paddedNum;

    let newLog : Types.AuditLog = {
      logId = logId;
      user = userPrincipal;
      action = action;
      timestamp = timestamp;
      details = details;
    };

    let existingLogs = switch (auditLogs.get(userPrincipal)) {
      case (?arr) { arr };
      case (null) { [] };
    };

    let updatedLogs = Array.append(existingLogs, [newLog]);
    auditLogs.put(userPrincipal, updatedLogs);

    return newLog;
  };
};
