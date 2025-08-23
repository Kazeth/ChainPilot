import Text "mo:base/Text";
import Nat "mo:base/Nat";
import Time "mo:base/Time";
import TrieMap "mo:base/TrieMap";
import Principal "mo:base/Principal";
import Iter "mo:base/Iter";
import Array "mo:base/Array";
import Types "../Types";
import WalletBackend "canister:wallet_backend";

persistent actor {
  var stableInsurances : [(Principal, [Types.Insurance])] = [];
  private transient var insurances = TrieMap.TrieMap<Principal, [Types.Insurance]>(Principal.equal, Principal.hash);

  system func preupgrade() {
    stableInsurances := Iter.toArray(insurances.entries());
  };

  system func postupgrade() {
    insurances := TrieMap.fromEntries<Principal, [Types.Insurance]>(Iter.fromArray(stableInsurances), Principal.equal, Principal.hash);
  };

  public query func getAllInsurances() : async [(Principal, [Types.Insurance])] {
    return Iter.toArray(insurances.entries());
  };

  public query func getInsurancesByPrincipal(principal : Principal) : async [Types.Insurance] {
    switch (insurances.get(principal)) {
      case null return [];
      case (?logs) return Iter.toArray(logs.vals());
    };
  };

  public query func getWalletInsurance(principal : Principal, walletAddress : Text) : async ?Types.Insurance {
    switch (insurances.get(principal)) {
      // Kalau principal punya daftar insurance
      case (?insuranceList) {
        // Cari di dalam array
        for (insurance in insuranceList.vals()) {
          if (insurance.walletAddress == walletAddress) {
            return ?insurance; // ditemukan
          };
        };
        return null; // principal ada, tapi wallet tidak ditemukan
      };
      // Kalau principal tidak ada di map
      case null {
        return null;
      };
    };
  };

  public func triggerInheritance(insurance : Types.Insurance) : async Nat {
    let userWallets = await WalletBackend.getWalletsByPrincipal(insurance.user);

    var sourceWallet : ?Types.Wallet = null;

    for (w in userWallets.vals()) {
      if (w.walletAddress == insurance.walletAddress) {
        sourceWallet := ?w;
      };
    };

    if (sourceWallet == null) {
      return 0; // source wallet not found
    };

    let src = switch sourceWallet { case (?s) s; case null return 0 };

    let allWallets = await WalletBackend.getAllWallets();
    var backupWallet : ?Types.Wallet = null;

    for ((_, walletArr) in allWallets.vals()) {
      for (w in walletArr.vals()) {
        if (w.walletAddress == insurance.backUpWalletAddress) {
          backupWallet := ?w;
        };
      };
    };

    if (backupWallet == null) {
      return 0; // backup wallet not found
    };

    let bWallet = switch backupWallet { case (?b) b; case null return 0 };

    let holdings = await WalletBackend.getHoldingsByWalletId(src.walletId);

    let newBalance = bWallet.balance + src.balance;

    let updatedWallet : Types.Wallet = {
      walletId = bWallet.walletId;
      walletAddress = bWallet.walletAddress;
      owner = bWallet.owner;
      blockchainNetwork = bWallet.blockchainNetwork;
      balance = newBalance;
      connectedExchange = bWallet.connectedExchange;
    };

    ignore await WalletBackend.updateWallet(updatedWallet);

    for ((_, hArr) in holdings.vals()) {
      for (h in hArr.vals()) {
        ignore await WalletBackend.addHoldingToUserWallet(
          bWallet.walletId,
          h.asset.assetId,
          h.amount,
          h.valueUSD,
        );
      };
    };

    ignore await WalletBackend.clearWallet(src.walletId);

    return 1; // sukses
  };

  public func insuranceCheck(insurance : Types.Insurance, currentDate : Time.Time) : async Text {
    if (insurance.warnCount >= 4) {
      let res : Nat = await triggerInheritance(insurance);
      if (res == 1) {
        let res2 : Text = await deleteInsurance(insurance);
        return "Succeed to inherit wallet";
      } else {
        return "Failed to inherit wallet";
      };
    };

    let reminderDate = insurance.dateStart + (insurance.interval * (insurance.warnCount + 1));
    if (reminderDate >= currentDate) {
      // trigger kirim email
      let res : Types.Insurance = await increaseInsuranceWarnCount(insurance);
      return "Remind user via email";
    } else {
      return "User's wallet still active";
    };
    return "Error occured while checking insurance";
  };

  public func deleteInsurance(insurance : Types.Insurance) : async Text {
    switch (insurances.get(insurance.user)) {
      case (?arr) {
        let filtered = Array.filter<Types.Insurance>(
          arr,
          func(x : Types.Insurance) : Bool {
            x.walletAddress != insurance.walletAddress;
          },
        );

        if (Array.size(filtered) > 0) {
          insurances.put(insurance.user, filtered);
        } else {
          ignore insurances.remove(insurance.user);
        };
        return "Insurance deleted";
      };
      case null {
        return "Insurance deletion failed";
      };
    };
  };

  public func increaseInsuranceWarnCount(
    insurance : Types.Insurance
  ) : async Types.Insurance {

    let newInsurance : Types.Insurance = {
      user = insurance.user;
      walletAddress = insurance.walletAddress;
      backUpWalletAddress = insurance.backUpWalletAddress;
      email = insurance.email;
      dateStart = insurance.dateStart;
      interval = insurance.interval;
      warnCount = insurance.warnCount + 1;
    };

    let existingInsurances = switch (insurances.get(insurance.user)) {
      case (?arr) { arr };
      case (null) { [] };
    };

    let updatedInsurances = Array.append(existingInsurances, [newInsurance]);
    insurances.put(insurance.user, updatedInsurances);

    return newInsurance;
  };

  public func createInsurance(
    userPrincipal : Principal,
    walletAddress : Text,
    backUpWalletAddress : Text,
    email : Text,
    dateStart : Time.Time,
    interval : Time.Time,
  ) : async Types.Insurance {

    let newInsurance : Types.Insurance = {
      user = userPrincipal;
      walletAddress = walletAddress;
      backUpWalletAddress = backUpWalletAddress;
      email = email;
      dateStart = dateStart;
      interval = interval;
      warnCount = 0;
    };

    let existingInsurances = switch (insurances.get(userPrincipal)) {
      case (?arr) { arr };
      case (null) { [] };
    };

    let updatedInsurances = Array.append(existingInsurances, [newInsurance]);
    insurances.put(userPrincipal, updatedInsurances);

    return newInsurance;
  };
};
