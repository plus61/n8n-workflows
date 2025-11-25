#!/usr/bin/env node

/**
 * Deploy Workflow
 * 
 * Deploy workflow to n8n instance with validation
 * Usage: node scripts/deploy.js <workflow-file> [--env=dev|staging|prod] [--activate]
 */

const fs = require('fs').promises;
const path = require('path');

// Configuration
const CONFIG = {
  environments: {
    dev: {
      name: 'Development',
      requireValidation: true,
      validationProfile: 'runtime',
      backupBeforeDeploy: false
    },
    staging: {
      name: 'Staging',
      requireValidation: true,
      validationProfile: 'strict',
      backupBeforeDeploy: true
    },
    prod: {
      name: 'Production',
      requireValidation: true,
      validationProfile: 'strict',
      backupBeforeDeploy: true
    }
  },
  defaultEnv: 'dev'
};

// Parse command line arguments
function parseArgs() {
  const args = process.argv.slice(2);
  
  if (args.length === 0 || args.includes('--help') || args.includes('-h')) {
    showHelp();
    process.exit(0);
  }
  
  const options = {
    workflowFile: args[0],
    env: CONFIG.defaultEnv,
    activate: false,
    skipValidation: false,
    force: false
  };
  
  for (let i = 1; i < args.length; i++) {
    const arg = args[i];
    
    if (arg.startsWith('--env=')) {
      options.env = arg.split('=')[1];
    } else if (arg === '--activate') {
      options.activate = true;
    } else if (arg === '--skip-validation') {
      options.skipValidation = true;
    } else if (arg === '--force') {
      options.force = true;
    }
  }
  
  // Validate environment
  if (!CONFIG.environments[options.env]) {
    console.error(`❌ Invalid environment: ${options.env}`);
    console.error(`Valid environments: ${Object.keys(CONFIG.environments).join(', ')}`);
    process.exit(1);
  }
  
  return options;
}

// Show help
function showHelp() {
  console.log(`
Deploy Workflow to n8n

Usage:
  node scripts/deploy.js <workflow-file> [options]

Options:
  --env=<environment>  Target environment (default: dev)
                       Options: dev, staging, prod
  --activate           Activate workflow after deployment
  --skip-validation    Skip pre-deployment validation (not recommended)
  --force              Force deployment even if validation warnings exist
  --help, -h           Show this help message

Examples:
  # Deploy to development
  node scripts/deploy.js workflows/development/my-workflow.json

  # Deploy to production and activate
  node scripts/deploy.js workflows/development/my-workflow.json --env=prod --activate

  # Force deploy (skip validation)
  node scripts/deploy.js workflows/development/my-workflow.json --skip-validation --force

Environment Settings:
  dev      - Development environment, runtime validation
  staging  - Staging environment, strict validation, backup enabled
  prod     - Production environment, strict validation, backup enabled
  `);
}

// Load workflow from file
async function loadWorkflow(filePath) {
  try {
    const content = await fs.readFile(filePath, 'utf8');
    return JSON.parse(content);
  } catch (error) {
    throw new Error(`Failed to load ${filePath}: ${error.message}`);
  }
}

// Validate workflow (mock implementation)
async function validateWorkflow(workflow, profile) {
  console.log(`\n🔍 Validating workflow (profile: ${profile})...`);
  
  const result = {
    valid: true,
    errors: [],
    warnings: [],
    suggestions: []
  };
  
  // Basic validation
  if (!workflow.name) {
    result.errors.push('Workflow name is required');
    result.valid = false;
  }
  
  if (!workflow.nodes || workflow.nodes.length === 0) {
    result.errors.push('Workflow must have at least one node');
    result.valid = false;
  }
  
  // Check for trigger
  const hasTrigger = workflow.nodes?.some(node => 
    node.type && (
      node.type.includes('Trigger') ||
      node.type.includes('webhook') ||
      node.type.includes('schedule')
    )
  );
  
  if (!hasTrigger) {
    if (profile === 'strict') {
      result.errors.push('Workflow must have at least one trigger node');
      result.valid = false;
    } else {
      result.warnings.push('No trigger node found');
    }
  }
  
  // Display results
  if (result.errors.length > 0) {
    console.log('\n❌ Validation Errors:');
    result.errors.forEach(err => console.log(`   - ${err}`));
  }
  
  if (result.warnings.length > 0) {
    console.log('\n⚠️  Validation Warnings:');
    result.warnings.forEach(warn => console.log(`   - ${warn}`));
  }
  
  if (result.valid && result.errors.length === 0 && result.warnings.length === 0) {
    console.log('✅ Validation passed');
  }
  
  return result;
}

// Backup existing workflow (mock implementation)
async function backupWorkflow(workflowId, env) {
  const backupDir = path.join(__dirname, '../workflows/backups', env);
  await fs.mkdir(backupDir, { recursive: true });
  
  const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
  const backupPath = path.join(backupDir, `workflow-${workflowId}-${timestamp}.json`);
  
  // In production, this would fetch from n8n API
  // For now, we'll just create a placeholder
  await fs.writeFile(backupPath, JSON.stringify({ 
    workflowId, 
    backedUpAt: new Date().toISOString() 
  }, null, 2), 'utf8');
  
  console.log(`📦 Backup created: ${path.basename(backupPath)}`);
  
  return backupPath;
}

// Deploy workflow (mock implementation)
async function deployWorkflow(workflow, env) {
  console.log(`\n🚀 Deploying to ${CONFIG.environments[env].name}...`);
  
  // Simulate API call
  await new Promise(resolve => setTimeout(resolve, 1000));
  
  const result = {
    id: `workflow-${Date.now()}`,
    name: workflow.name,
    url: `https://n8n-${env}.example.com/workflow/${Date.now()}`,
    webhookUrl: workflow.nodes?.some(n => n.type?.includes('webhook')) 
      ? `https://n8n-${env}.example.com/webhook/${Date.now()}`
      : null,
    active: false
  };
  
  console.log(`✅ Deployed successfully`);
  console.log(`   ID: ${result.id}`);
  console.log(`   URL: ${result.url}`);
  if (result.webhookUrl) {
    console.log(`   Webhook URL: ${result.webhookUrl}`);
  }
  
  return result;
}

// Activate workflow (mock implementation)
async function activateWorkflow(workflowId) {
  console.log(`\n⚡ Activating workflow...`);
  
  // Simulate API call
  await new Promise(resolve => setTimeout(resolve, 500));
  
  console.log(`✅ Workflow activated`);
}

// Save deployment metadata
async function saveDeploymentMetadata(workflow, deployment, env, backupPath) {
  const metadataDir = path.join(__dirname, '../workflows/production/metadata');
  await fs.mkdir(metadataDir, { recursive: true });
  
  const metadata = {
    workflowId: deployment.id,
    workflowName: workflow.name,
    environment: env,
    deployedAt: new Date().toISOString(),
    deployedBy: process.env.USER || 'unknown',
    url: deployment.url,
    webhookUrl: deployment.webhookUrl,
    active: deployment.active,
    backupPath: backupPath,
    nodes: workflow.nodes?.length || 0,
    version: workflow.version || '1.0'
  };
  
  const metadataPath = path.join(metadataDir, `${deployment.id}.json`);
  await fs.writeFile(metadataPath, JSON.stringify(metadata, null, 2), 'utf8');
  
  console.log(`\n📄 Metadata saved: ${path.basename(metadataPath)}`);
  
  return metadata;
}

// Prompt for confirmation
function promptConfirmation(message) {
  return new Promise((resolve) => {
    const readline = require('readline').createInterface({
      input: process.stdin,
      output: process.stdout
    });
    
    readline.question(`${message} (y/N): `, (answer) => {
      readline.close();
      resolve(answer.toLowerCase() === 'y' || answer.toLowerCase() === 'yes');
    });
  });
}

// Main function
async function main() {
  const options = parseArgs();
  const envConfig = CONFIG.environments[options.env];
  
  console.log('🚀 n8n Workflow Deployment\n');
  console.log(`File: ${options.workflowFile}`);
  console.log(`Environment: ${envConfig.name}`);
  console.log(`Activate: ${options.activate ? 'Yes' : 'No'}`);
  console.log('');
  
  // Load workflow
  console.log('📂 Loading workflow...');
  const workflow = await loadWorkflow(options.workflowFile);
  console.log(`✅ Loaded: ${workflow.name}`);
  console.log(`   Nodes: ${workflow.nodes?.length || 0}`);
  console.log(`   Connections: ${Object.keys(workflow.connections || {}).length}`);
  
  // Validation
  if (!options.skipValidation && envConfig.requireValidation) {
    const validation = await validateWorkflow(workflow, envConfig.validationProfile);
    
    if (!validation.valid) {
      console.error('\n❌ Validation failed. Deployment aborted.');
      console.error('   Use --force to deploy anyway (not recommended)');
      process.exit(1);
    }
    
    if (validation.warnings.length > 0 && !options.force) {
      console.warn('\n⚠️  Validation warnings detected.');
      const proceed = await promptConfirmation('Continue deployment?');
      if (!proceed) {
        console.log('Deployment cancelled.');
        process.exit(0);
      }
    }
  } else if (options.skipValidation) {
    console.warn('\n⚠️  Validation skipped (not recommended)');
  }
  
  // Backup
  let backupPath = null;
  if (envConfig.backupBeforeDeploy) {
    // In production, check if workflow exists first
    // For now, always create backup
    backupPath = await backupWorkflow('existing-workflow-id', options.env);
  }
  
  // Confirm deployment to production
  if (options.env === 'prod' && !options.force) {
    console.warn('\n⚠️  PRODUCTION DEPLOYMENT');
    const proceed = await promptConfirmation('Are you sure you want to deploy to production?');
    if (!proceed) {
      console.log('Deployment cancelled.');
      process.exit(0);
    }
  }
  
  // Deploy
  const deployment = await deployWorkflow(workflow, options.env);
  
  // Activate
  if (options.activate) {
    await activateWorkflow(deployment.id);
    deployment.active = true;
  }
  
  // Save metadata
  await saveDeploymentMetadata(workflow, deployment, options.env, backupPath);
  
  // Success summary
  console.log('\n' + '='.repeat(50));
  console.log('✅ Deployment Complete');
  console.log('='.repeat(50));
  console.log(`Workflow ID: ${deployment.id}`);
  console.log(`Status: ${deployment.active ? 'Active' : 'Inactive'}`);
  console.log(`URL: ${deployment.url}`);
  if (deployment.webhookUrl) {
    console.log(`Webhook URL: ${deployment.webhookUrl}`);
  }
  console.log('='.repeat(50));
  
  // Next steps
  console.log('\n📋 Next Steps:');
  if (!deployment.active) {
    console.log('   1. Test the workflow manually');
    console.log('   2. Activate: node scripts/deploy.js <file> --activate');
  } else {
    console.log('   1. Monitor execution logs');
    console.log('   2. Check for errors in n8n dashboard');
  }
  console.log('');
}

// Run
main().catch(error => {
  console.error('\n❌ Deployment failed:', error.message);
  process.exit(1);
});
