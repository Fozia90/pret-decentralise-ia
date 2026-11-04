// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract CreditLoanV2 {
    address public owner;
    address public authorizedScorer;

    uint256 public nextLoanId;

    struct Loan {
        address borrower;
        uint256 amount;
        uint256 collateral;
        uint256 interestRate;
        uint256 creditScore;
        uint256 amountRepaid;
        bool active;
    }

    mapping(uint256 => Loan) public loans;
    mapping(bytes32 => bool) public usedScores;

    event ScorerUpdated(address indexed scorer);

    event LoanCreated(
        uint256 indexed loanId,
        address indexed borrower,
        uint256 amount,
        uint256 collateral,
        uint256 creditScore,
        uint256 interestRate
    );

    event RepaymentMade(
        uint256 indexed loanId,
        address indexed borrower,
        uint256 amount
    );

    event LoanClosed(uint256 indexed loanId);

    modifier onlyOwner() {
        require(msg.sender == owner, "Owner uniquement");
        _;
    }

    constructor(address _authorizedScorer) {
        require(
            _authorizedScorer != address(0),
            "Adresse du score invalide"
        );

        owner = msg.sender;
        authorizedScorer = _authorizedScorer;
    }

    function setAuthorizedScorer(
        address _newScorer
    ) external onlyOwner {
        require(
            _newScorer != address(0),
            "Adresse invalide"
        );

        authorizedScorer = _newScorer;
        emit ScorerUpdated(_newScorer);
    }

    function getInterestRate(
        uint256 _score
    ) public pure returns (uint256) {
        require(_score <= 100, "Score invalide");

        if (_score >= 80) {
            return 5;
        } else if (_score >= 60) {
            return 10;
        } else if (_score >= 40) {
            return 15;
        } else {
            return 20;
        }
    }

    function requestLoan(
        uint256 _amount,
        uint256 _score,
        uint256 _deadline,
        bytes calldata _signature
    ) external payable {
        require(_amount > 0, "Montant invalide");
        require(msg.value > 0, "Garantie obligatoire");
        require(_score <= 100, "Score invalide");
        require(block.timestamp <= _deadline, "Signature expiree");

        bytes32 messageHash = keccak256(
            abi.encode(
                address(this),
                block.chainid,
                msg.sender,
                _amount,
                _score,
                _deadline
            )
        );

        bytes32 ethSignedHash = keccak256(
            abi.encodePacked(
                "\x19Ethereum Signed Message:\n32",
                messageHash
            )
        );

        require(
            recoverSigner(ethSignedHash, _signature)
                == authorizedScorer,
            "Signature du score invalide"
        );

        require(
            !usedScores[messageHash],
            "Score deja utilise"
        );

        usedScores[messageHash] = true;

        uint256 rate = getInterestRate(_score);
        uint256 loanId = nextLoanId++;

        loans[loanId] = Loan({
            borrower: msg.sender,
            amount: _amount,
            collateral: msg.value,
            interestRate: rate,
            creditScore: _score,
            amountRepaid: 0,
            active: true
        });

        emit LoanCreated(
            loanId,
            msg.sender,
            _amount,
            msg.value,
            _score,
            rate
        );
    }

    function repayLoan(
        uint256 _loanId
    ) external payable {
        Loan storage loan = loans[_loanId];

        require(loan.active, "Pret inactif");
        require(
            msg.sender == loan.borrower,
            "Emprunteur uniquement"
        );
        require(msg.value > 0, "Paiement invalide");

        uint256 totalDue =
            loan.amount +
            (loan.amount * loan.interestRate / 100);

        require(
            loan.amountRepaid + msg.value <= totalDue,
            "Paiement superieur au solde"
        );

        loan.amountRepaid += msg.value;

        emit RepaymentMade(
            _loanId,
            msg.sender,
            msg.value
        );

        if (loan.amountRepaid == totalDue) {
            loan.active = false;
            emit LoanClosed(_loanId);
        }
    }

    function recoverSigner(
        bytes32 _hash,
        bytes calldata _signature
    ) public pure returns (address) {
        require(
            _signature.length == 65,
            "Signature incorrecte"
        );

        bytes32 r;
        bytes32 s;
        uint8 v;

        assembly {
            r := calldataload(_signature.offset)
            s := calldataload(add(_signature.offset, 32))
            v := byte(
                0,
                calldataload(add(_signature.offset, 64))
            )
        }

        if (v < 27) {
            v += 27;
        }

        require(v == 27 || v == 28, "Valeur v invalide");

        return ecrecover(_hash, v, r, s);
    }
}