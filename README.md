# Solana Token Info Bot

A Telegram bot that provides detailed information about Solana tokens using their addresses.

## Features

- Token information lookup using Solana addresses
- Real-time price and market data from DexScreener
- Backup data from pump.fun API
- Token details including:
  - Name and symbol
  - Current price and 24h change
  - Trading volume and liquidity
  - Market cap (when available)
  - Number of holders
  - Social media links
  - Trading platform links

## Usage

1. Start a chat with [@QTtrades_bot](https://t.me/QTtrades_bot) on Telegram
2. Send a valid Solana token address
3. Receive comprehensive token information and market data

Example token address:
`EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v` (USDC)

## Commands

- `/start` - Initialize the bot and get a welcome message
- `/help` - View usage instructions and supported features
- Simply send any valid Solana token address to get information

## Technical Details

The bot utilizes multiple APIs to gather comprehensive token information:

- DexScreener API for real-time market data
- pump.fun API as a backup data source
- Solana blockchain data

## Error Handling

- Validates Solana addresses before processing
- Gracefully handles API failures with fallback options
- Returns clear error messages for invalid inputs

## License

This project is licensed under the MIT License - see the LICENSE file for details.
