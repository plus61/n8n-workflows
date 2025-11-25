#!/usr/bin/env node

/**
 * Backup Workflows
 * 
 * Backup workflows from n8n instance
 * Usage: node scripts/backup.js [--all] [--id=workflow_id] [--env=prod]
 */

const fs = require('fs').promises;
const path = require('path');

// Configuration
const CONFIG = {
  backupDir: path.join(__dirname, '../workflows/backups'),
  environments: ['dev', 'staging', 'prod'],
  defaultEnv: 'prod'
};

// Parse command line arguments
function parseArgs() {
  const args = process.argv.slice(2);
  
  if (args.includes('--help') || args.includes('-h')) {
    showHelp();
    process.exit(0);
  }
  
  const options = {
    all: false,
    workflowId: null,
    env: CONFIG.defaultEnv,
    includeExecutions: false,
    compress: false
  };
  
  for (const arg of args) {
    if (arg === '--all') {
      options.all = true;
    } else if (arg.startsWith('--id=')) {
      options.workflowId = arg.split('=')[1];
    } else if (arg.startsWith('--env=')) {
      options.env = arg.split('=')[1];
    } else if (arg === '--include-executions') {
      options.includeExecutions = true;
    } else if (arg === '--compress') {
      options.compress = true;
    }
  }
  
  // Validate
  if (!options.all && !options.workflowId) {
    console.error('❌ Must specify either --all or --id=<workflow_id>');
    showHelp();
    process.exit(1);
  }
  
  if (!CONFIG.environments.includes(options.env)) {
    console.error(`❌ Invalid environment: ${options.env}`);
    console.error(`Valid environments: ${CONFIG.environments.join(', ')}`);
    process.exit(1);
  }
  
  return options;
}

// Show help
function showHelp() {
  console.log(`
Backup n8n Workflows

Usage:
  node scripts/backup.js [options]

Options:
  --all                    Backup all workflows
  --id=<workflow_id>       Backup specific workflow by ID
  --env=<environment>      Source environment (default: prod)
  --include-executions     Include execution history
  --compress               Compress backup files
  --help, -h               Show this help message

Examples:
  # Backup all production workflows
  node scripts/backup.js --all

  # Backup specific workflow
  node scripts/backup.js --id=workflow_123

  # Backup from staging with executions
  node scripts/backup.js --all --env=staging --include-executions

  # Compressed backup
  node scripts/backup.js --all --compress
  `);
}

// Get all workflows (mock implementation)
async function getAllWorkflows(env) {
  // In production, this would call n8n API
  // For now, return mock data
  return [
    {
      id: 'workflow-1',
      name: 'Email Processor',
      active: true,
      nodes: [],
      connections: {}
    },
    {
      id: 'workflow-2',
      name: 'Video Generator',
      active: false,
      nodes: [],
      connections: {}
    }
  ];
}

// Get single workflow (mock implementation)
async function getWorkflow(workflowId, env) {
  // In production, this would call n8n API
  return {
    id: workflowId,
    name: 'Sample Workflow',
    active: true,
    nodes: [],
    connections: {},
    settings: {}
  };
}

// Get workflow executions (mock implementation)
async function getWorkflowExecutions(workflowId, env) {
  // In production, this would call n8n API
  return [
    {
      id: 'exec-1',
      workflowId: workflowId,
      status: 'success',
      startedAt: new Date().toISOString()
    }
  ];
}

// Save backup
async function saveBackup(workflow, executions, env, compress) {
  const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
  const envDir = path.join(CONFIG.backupDir, env);
  await fs.mkdir(envDir, { recursive: true });
  
  const backup = {
    workflow: workflow,
    executions: executions || [],
    backedUpAt: new Date().toISOString(),
    environment: env,
    version: '1.0'
  };
  
  const fileName = `${workflow.id}-${timestamp}.json`;
  const filePath = path.join(envDir, fileName);
  
  await fs.writeFile(filePath, JSON.stringify(backup, null, 2), 'utf8');
  
  let size = (await fs.stat(filePath)).size;
  
  // Compress if requested
  if (compress) {
    // In production, use actual compression
    console.log(`📦 Would compress ${fileName} (not implemented in demo)`);
  }
  
  return {
    path: filePath,
    size: size,
    compressed: compress
  };
}

// Format file size
function formatSize(bytes) {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(2)} KB`;
  return `${(bytes / 1024 / 1024).toFixed(2)} MB`;
}

// Main function
async function main() {
  const options = parseArgs();
  
  console.log('💾 n8n Workflow Backup\n');
  console.log(`Environment: ${options.env}`);
  console.log(`Mode: ${options.all ? 'All workflows' : `Single workflow (${options.workflowId})`}`);
  console.log(`Include executions: ${options.includeExecutions ? 'Yes' : 'No'}`);
  console.log(`Compress: ${options.compress ? 'Yes' : 'No'}`);
  console.log('');
  
  const results = {
    total: 0,
    successful: 0,
    failed: 0,
    totalSize: 0
  };
  
  try {
    let workflows = [];
    
    if (options.all) {
      console.log('📥 Fetching all workflows...');
      workflows = await getAllWorkflows(options.env);
      console.log(`✅ Found ${workflows.length} workflow(s)\n`);
    } else {
      console.log(`📥 Fetching workflow ${options.workflowId}...`);
      const workflow = await getWorkflow(options.workflowId, options.env);
      workflows = [workflow];
      console.log(`✅ Workflow found: ${workflow.name}\n`);
    }
    
    results.total = workflows.length;
    
    // Backup each workflow
    for (const workflow of workflows) {
      try {
        console.log(`📦 Backing up: ${workflow.name} (${workflow.id})`);
        
        // Get executions if requested
        let executions = null;
        if (options.includeExecutions) {
          console.log('   Fetching executions...');
          executions = await getWorkflowExecutions(workflow.id, options.env);
          console.log(`   Found ${executions.length} execution(s)`);
        }
        
        // Save backup
        const backup = await saveBackup(
          workflow,
          executions,
          options.env,
          options.compress
        );
        
        console.log(`   ✅ Saved: ${path.basename(backup.path)}`);
        console.log(`   Size: ${formatSize(backup.size)}\n`);
        
        results.successful++;
        results.totalSize += backup.size;
        
      } catch (error) {
        console.error(`   ❌ Failed: ${error.message}\n`);
        results.failed++;
      }
    }
    
  } catch (error) {
    console.error(`❌ Backup failed: ${error.message}`);
    process.exit(1);
  }
  
  // Summary
  console.log('─'.repeat(50));
  console.log('Summary:');
  console.log(`  Total workflows: ${results.total}`);
  console.log(`  Successful: ${results.successful}`);
  console.log(`  Failed: ${results.failed}`);
  console.log(`  Total size: ${formatSize(results.totalSize)}`);
  console.log(`  Location: ${CONFIG.backupDir}/${options.env}`);
  console.log('─'.repeat(50));
  
  if (results.failed > 0) {
    process.exit(1);
  }
}

// Run
main().catch(error => {
  console.error('Fatal error:', error);
  process.exit(1);
});
