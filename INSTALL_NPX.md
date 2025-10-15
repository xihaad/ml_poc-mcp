# Installing npx (Node.js) on Linux

## Quick Install (Recommended)

Run these commands in your terminal:

```bash
# Option 1: Using the provided script
chmod +x install_nodejs.sh
./install_nodejs.sh
```

## Manual Installation Options

### Option 1: NodeSource Repository (Latest LTS - Recommended)
```bash
# Download and run NodeSource setup
curl -fsSL https://deb.nodesource.com/setup_lts.x | sudo -E bash -

# Install Node.js (includes npm and npx)
sudo apt-get install -y nodejs

# Verify installation
node --version
npm --version
npx --version
```

### Option 2: Using Snap (Simple)
```bash
# Install Node.js via snap
sudo snap install node --classic

# Verify installation
node --version
npm --version
npx --version
```

### Option 3: Using APT (Older version, but stable)
```bash
# Update package list
sudo apt update

# Install Node.js and npm
sudo apt install -y nodejs npm

# Verify installation
node --version
npm --version
npx --version
```

### Option 4: Using NVM (Node Version Manager - Best for developers)
```bash
# Install NVM
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash

# Reload your shell configuration
source ~/.bashrc

# Install latest LTS Node.js
nvm install --lts

# Use the installed version
nvm use --lts

# Verify installation
node --version
npm --version
npx --version
```

## After Installation

1. **Restart your terminal** or run:
   ```bash
   source ~/.bashrc
   ```

2. **Verify npx is installed:**
   ```bash
   npx --version
   ```

3. **Test your MCP server:**
   ```bash
   mcp dev server_setup/server.py
   ```

## Troubleshooting

### If npx is still not found after installation:

1. **Check if Node.js is in your PATH:**
   ```bash
   which node
   which npm
   which npx
   ```

2. **Add Node.js to PATH manually (if needed):**
   ```bash
   echo 'export PATH="/usr/bin/node:$PATH"' >> ~/.bashrc
   source ~/.bashrc
   ```

3. **For snap installation, ensure snap bin is in PATH:**
   ```bash
   echo 'export PATH="/snap/bin:$PATH"' >> ~/.bashrc
   source ~/.bashrc
   ```

### If you get permission errors:

Run commands with `sudo` or fix npm permissions:
```bash
mkdir ~/.npm-global
npm config set prefix '~/.npm-global'
echo 'export PATH=~/.npm-global/bin:$PATH' >> ~/.bashrc
source ~/.bashrc
```

## Quick Test

After installation, test that everything works:

```bash
# Test Node.js
node -e "console.log('Node.js works!')"

# Test npm
npm --version

# Test npx
npx --version

# Test your MCP server
cd /home/ahmed/Projects/MCP/ml_poc-mcp
mcp dev server_setup/server.py
```

## Expected Versions

After successful installation, you should see versions like:
- Node.js: v18.x.x or v20.x.x (LTS versions)
- npm: 9.x.x or 10.x.x
- npx: 9.x.x or 10.x.x

If all three commands return version numbers, you're ready to use MCP!
