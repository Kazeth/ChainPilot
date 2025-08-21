import Text "mo:base/Text";
import TrieMap "mo:base/TrieMap";
import Principal "mo:base/Principal";
import Iter "mo:base/Iter";
import Types "../Types";

persistent actor {

  var stableUsers : [(Principal, Types.User)] = [];
  private transient var users = TrieMap.TrieMap<Principal, Types.User>(Principal.equal, Principal.hash);

  system func preupgrade() {
    stableUsers := Iter.toArray(users.entries());
  };

  system func postupgrade() {
    users := TrieMap.fromEntries<Principal, Types.User>(Iter.fromArray(stableUsers), Principal.equal, Principal.hash);
  };

  public query func getAllUserData() : async [(Principal, Types.User)] {
    return Iter.toArray(users.entries());
  };

  public query func getUserData(principal : Principal) : async ?Types.User {
    return users.get(principal);
  };

  public func createUser(
    userPrincipal : Principal,
    userName : Text,
    userEmail : Text,
  ) : async Types.User {

    let empty : Text = "";
    let emptyHolding : [Types.Holding] = [];

    let newUser : Types.User = {
      user = userPrincipal;
      username = userName;
      email = userEmail;
      walletAddress = empty;
      portfolio = emptyHolding;
    };
    users.put(userPrincipal, newUser);

    return newUser;
  };

};
