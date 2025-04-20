// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;
 
contract GameReward {
    address public owner;
    uint256 public rewardAmount;
 
    event RewardClaimed(address indexed user, uint256 amount);
    event RewardAmountUpdated(uint256 newAmount);
    event FundsWithdrawn(address to, uint256 amount);
    event Funded(address from, uint256 amount);
 
    constructor(uint256 _rewardAmount) {
        owner = msg.sender;
        rewardAmount = _rewardAmount;
    }
 
    // Fallback to accept funds
    receive() external payable {
        emit Funded(msg.sender, msg.value);
    }
 
    // Reward a user (now callable by anyone)
    function rewardUser(address payable user) external {
        require(user != address(0), "Cannot reward zero address");
        require(address(this).balance >= rewardAmount, "Insufficient funds in contract");
 
        (bool success, ) = user.call{value: rewardAmount}("");
        require(success, "Reward transfer failed");
 
        emit RewardClaimed(user, rewardAmount);
    }
 
    // Update the reward amount (now callable by anyone)
    function setRewardAmount(uint256 _rewardAmount) external {
        rewardAmount = _rewardAmount;
        emit RewardAmountUpdated(_rewardAmount);
    }
 
    // Withdraw all funds (now callable by anyone)
    function withdraw() external {
        uint256 balance = address(this).balance;
        require(balance > 0, "Nothing to withdraw");
 
        (bool success, ) = payable(msg.sender).call{value: balance}("");
        require(success, "Withdraw failed");
 
        emit FundsWithdrawn(msg.sender, balance);
    }
 
    // Get contract balance (view function)
    function getBalance() external view returns (uint256) {
        return address(this).balance;
    }
 
    // Accept deposits with an explicit function call
    function deposit() external payable {
        emit Funded(msg.sender, msg.value);
    }
}