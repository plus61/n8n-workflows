#!/usr/bin/env node

/**
 * Validate All Workflows
 * 
 * Validates all workflows in the development directory
 * Usage: node scripts/validate-all.js [--profile=runtime] [--autofix]
 */

const fs = require('fs').promises;
const path = require('path');

// Configuration
const CONFIG = {
  workflowsDir: path.join(__dirname, '../workflows/development'),
  profiles: ['minimal', 'runtime', 'ai-friendly', 'strict'],
  defaultProfile: 'runtime'
};

// Parse command line arguments
function parseArgs() {
  const args = process.argv.slice(2);
  const options = {
    profile: CONFIG.defaultProfile,
    autofix: false,
    verbose: false
  };
  
  for (const arg of args) {
    if (arg.startsWith('--profile=')) {
      options.profile = arg.split('=')[1];
    } else if (arg === '--autofix') {
      options.autofix = true;
    } else if (arg === '--verbose' || arg === '-v') {
      options.verbose = true;
    } else if (arg === '--help' || arg === '-h') {
      showHelp();
      process.exit(0);
    }
  }
  
  // Validate profile
  if (!CONFIG.profiles.includes(options.profile)) {
    console.error(`❌ Invalid profile: ${options.profile}`);
    console.error(`Valid profiles: ${CONFIG.profiles.join(', ')}`);
    process.exit(1);
  }
  
  return options;
}

// Show help
function showHelp() {
  console.log(`
Validate All Workflows

Usage:
  node scripts/validate-all.js [options]

Options:
  --profile=<profile>  Validation profile (default: runtime)
                       Options: ${CONFIG.profiles.join(', ')}
  --autofix            Auto-fix common issues (preview mode)
  --verbose, -v        Show detailed validation results
  --help, -h           Show this help message

Examples:
  node scripts/validate-all.js
  node scripts/validate-all.js --profile=strict
  node scripts/validate-all.js --autofix --verbose

Validation Profiles:
  minimal      - Basic validation only
  runtime      - Standard validation (recommended)
  ai-friendly  - Flexible with helpful suggestions
  strict       - Production-ready validation
  `);
}

// Find all workflow JSON files
async function findWorkflowFiles(dir) {
  const files = [];
  
  try {
    const entries = await fs.readdir(dir, { withFileTypes: true });
    
    for (const entry of entries) {
      const fullPath = path.join(dir, entry.name);
      
      if (entry.isDirectory()) {
        // Recursively search subdirectories
        const subFiles = await findWorkflowFiles(fullPath);
        files.push(...subFiles);
      } else if (entry.isFile() && entry.name.endsWith('.json')) {
        files.push(fullPath);
      }
    }
  } catch (error) {
    if (error.code !== 'ENOENT') {
      console.error(`Error reading directory ${dir}:`, error.message);
    }
  }
  
  return files;
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

// Validate workflow (mock implementation - use actual MCP in production)
async function validateWorkflow(workflow, profile) {
  // In production, this would call the n8n-workflows MCP
  // For now, we'll do basic validation
  
  const result = {
    valid: true,
    errors: [],
    warnings: [],
    suggestions: []
  };
  
  // Check required fields
  if (!workflow.name) {
    result.errors.push('Workflow name is required');
    result.valid = false;
  }
  
  if (!workflow.nodes || !Array.isArray(workflow.nodes)) {
    result.errors.push('Workflow must have nodes array');
    result.valid = false;
  }
  
  if (!workflow.connections || typeof workflow.connections !== 'object') {
    result.errors.push('Workflow must have connections object');
    result.valid = false;
  }
  
  // Check nodes
  if (workflow.nodes) {
    const hasTrigger = workflow.nodes.some(node => 
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
    
    // Check node IDs
    const nodeIds = new Set();
    for (const node of workflow.nodes) {
      if (!node.id) {
        result.errors.push(`Node missing ID: ${node.name || 'unknown'}`);
        result.valid = false;
      } else if (nodeIds.has(node.id)) {
        result.errors.push(`Duplicate node ID: ${node.id}`);
        result.valid = false;
      } else {
        nodeIds.add(node.id);
      }
    }
  }
  
  // Check connections
  if (workflow.connections && workflow.nodes) {
    const nodeIds = new Set(workflow.nodes.map(n => n.id));
    
    for (const [sourceId, connections] of Object.entries(workflow.connections)) {
      if (!nodeIds.has(sourceId)) {
        result.errors.push(`Connection references non-existent source node: ${sourceId}`);
        result.valid = false;
      }
      
      if (connections.main && Array.isArray(connections.main)) {
        for (const outputConnections of connections.main) {
          if (Array.isArray(outputConnections)) {
            for (const conn of outputConnections) {
              if (!nodeIds.has(conn.node)) {
                result.errors.push(`Connection references non-existent target node: ${conn.node}`);
                result.valid = false;
              }
            }
          }
        }
      }
    }
  }
  
  // Add suggestions based on profile
  if (profile === 'ai-friendly' || profile === 'runtime') {
    if (workflow.nodes && workflow.nodes.length > 20) {
      result.suggestions.push('Consider splitting into sub-workflows (>20 nodes)');
    }
  }
  
  return result;
}

// Auto-fix common issues
async function autofixWorkflow(workflow) {
  const fixes = [];
  let modified = false;
  
  // Fix: Add missing IDs
  if (workflow.nodes) {
    for (let i = 0; i < workflow.nodes.length; i++) {
      const node = workflow.nodes[i];
      if (!node.id) {
        node.id = `node-${i}`;
        fixes.push(`Added ID to node: ${node.name || `node-${i}`}`);
        modified = true;
      }
    }
  }
  
  // Fix: Remove invalid connections
  if (workflow.connections && workflow.nodes) {
    const nodeIds = new Set(workflow.nodes.map(n => n.id));
    
    for (const [sourceId, connections] of Object.entries(workflow.connections)) {
      if (!nodeIds.has(sourceId)) {
        delete workflow.connections[sourceId];
        fixes.push(`Removed connection from non-existent node: ${sourceId}`);
        modified = true;
      }
    }
  }
  
  return { workflow, fixes, modified };
}

// Format validation result
function formatResult(filePath, result, verbose) {
  const fileName = path.basename(filePath);
  
  if (result.valid) {
    console.log(`✅ ${fileName}`);
  } else {
    console.log(`❌ ${fileName}`);
  }
  
  if (verbose || !result.valid) {
    if (result.errors.length > 0) {
      console.log(`   Errors (${result.errors.length}):`);
      result.errors.forEach(err => console.log(`     - ${err}`));
    }
    
    if (result.warnings.length > 0) {
      console.log(`   Warnings (${result.warnings.length}):`);
      result.warnings.forEach(warn => console.log(`     - ${warn}`));
    }
    
    if (verbose && result.suggestions.length > 0) {
      console.log(`   Suggestions (${result.suggestions.length}):`);
      result.suggestions.forEach(sug => console.log(`     - ${sug}`));
    }
  }
}

// Main function
async function main() {
  const options = parseArgs();
  
  console.log('🔍 Validating Workflows\n');
  console.log(`Profile: ${options.profile}`);
  console.log(`Directory: ${CONFIG.workflowsDir}`);
  console.log(`Auto-fix: ${options.autofix ? 'enabled' : 'disabled'}\n`);
  
  // Find all workflow files
  const files = await findWorkflowFiles(CONFIG.workflowsDir);
  
  if (files.length === 0) {
    console.log('No workflow files found.');
    return;
  }
  
  console.log(`Found ${files.length} workflow(s)\n`);
  
  // Validate each workflow
  const results = {
    total: files.length,
    valid: 0,
    invalid: 0,
    fixed: 0
  };
  
  for (const filePath of files) {
    try {
      let workflow = await loadWorkflow(filePath);
      
      // Auto-fix if requested
      if (options.autofix) {
        const { workflow: fixed, fixes, modified } = await autofixWorkflow(workflow);
        workflow = fixed;
        
        if (modified) {
          await fs.writeFile(filePath, JSON.stringify(workflow, null, 2), 'utf8');
          results.fixed++;
          console.log(`🔧 ${path.basename(filePath)} (${fixes.length} fixes applied)`);
          if (options.verbose) {
            fixes.forEach(fix => console.log(`     - ${fix}`));
          }
        }
      }
      
      // Validate
      const result = await validateWorkflow(workflow, options.profile);
      
      if (result.valid) {
        results.valid++;
      } else {
        results.invalid++;
      }
      
      formatResult(filePath, result, options.verbose);
      
    } catch (error) {
      console.log(`❌ ${path.basename(filePath)}`);
      console.log(`   Error: ${error.message}`);
      results.invalid++;
    }
    
    console.log(''); // Empty line between results
  }
  
  // Summary
  console.log('─'.repeat(50));
  console.log('Summary:');
  console.log(`  Total:   ${results.total}`);
  console.log(`  Valid:   ${results.valid} (${(results.valid/results.total*100).toFixed(1)}%)`);
  console.log(`  Invalid: ${results.invalid} (${(results.invalid/results.total*100).toFixed(1)}%)`);
  if (options.autofix) {
    console.log(`  Fixed:   ${results.fixed}`);
  }
  console.log('─'.repeat(50));
  
  // Exit code
  process.exit(results.invalid > 0 ? 1 : 0);
}

// Run
main().catch(error => {
  console.error('Fatal error:', error);
  process.exit(1);
});
