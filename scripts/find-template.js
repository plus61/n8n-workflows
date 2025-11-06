#!/usr/bin/env node
/**
 * n8n Template Search CLI
 *
 * Interactive search tool for finding n8n community templates
 *
 * Usage:
 *   node scripts/find-template.js "video automation"
 *   node scripts/find-template.js --category ai-video
 *   node scripts/find-template.js --interactive
 */

const fs = require('fs');
const path = require('path');
const readline = require('readline');

const INDEX_PATH = path.join(__dirname, '..', 'templates', '00-index.json');

/**
 * Load template index
 */
function loadIndex() {
  if (!fs.existsSync(INDEX_PATH)) {
    console.error('❌ Index not found. Run: node scripts/build-template-index.js');
    process.exit(1);
  }

  return JSON.parse(fs.readFileSync(INDEX_PATH, 'utf-8'));
}

/**
 * Search templates by query
 */
function searchTemplates(index, query) {
  const lowerQuery = query.toLowerCase();
  const results = [];

  index.categories.forEach(category => {
    category.templates.forEach(template => {
      const nameMatch = template.name.toLowerCase().includes(lowerQuery);
      const descMatch = template.description.toLowerCase().includes(lowerQuery);
      const tagMatch = category.tags.some(tag => tag.includes(lowerQuery));

      if (nameMatch || descMatch || tagMatch) {
        results.push({
          ...template,
          category: category.name,
          categoryDisplay: category.displayName,
          relevance: nameMatch ? 1.0 : (descMatch ? 0.7 : 0.5)
        });
      }
    });
  });

  return results.sort((a, b) => b.relevance - a.relevance);
}

/**
 * Search by category
 */
function searchByCategory(index, categoryName) {
  const category = index.categories.find(c => c.name === categoryName);

  if (!category) {
    console.error(`❌ Category not found: ${categoryName}`);
    console.log('\nAvailable categories:');
    index.categories.forEach(c => {
      console.log(`  - ${c.name} (${c.templateCount} templates)`);
    });
    return [];
  }

  return category.templates.map(t => ({
    ...t,
    category: category.name,
    categoryDisplay: category.displayName
  }));
}

/**
 * Display search results
 */
function displayResults(results, limit = 10) {
  if (results.length === 0) {
    console.log('❌ No templates found');
    return;
  }

  console.log(`\n✅ Found ${results.length} templates (showing ${Math.min(limit, results.length)})\n`);
  console.log('='.repeat(80));

  results.slice(0, limit).forEach((t, i) => {
    console.log(`\n${i + 1}. ${t.name}`);
    console.log(`   📁 Category: ${t.categoryDisplay}`);
    console.log(`   🆔 ID: ${t.id}`);
    console.log(`   🔧 Nodes: ${t.nodeCount}`);
    console.log(`   👁️  Views: ${t.popularity.toLocaleString()}`);
    if (t.description) {
      console.log(`   📝 ${t.description.substring(0, 120)}...`);
    }
  });

  console.log('\n' + '='.repeat(80));
}

/**
 * Interactive search mode
 */
async function interactiveSearch(index) {
  const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout
  });

  return new Promise((resolve) => {
    rl.question('🔍 What type of workflow are you looking for? ', (query) => {
      if (!query.trim()) {
        console.log('❌ No query provided');
        rl.close();
        resolve();
        return;
      }

      const results = searchTemplates(index, query);
      displayResults(results, 10);

      if (results.length > 0) {
        console.log('\n💡 Next steps:');
        console.log(`   - View details: node scripts/download-template.js ${results[0].id}`);
        console.log(`   - Search more: node scripts/find-template.js "${query}"`);
      }

      rl.close();
      resolve();
    });
  });
}

/**
 * Main execution
 */
async function main() {
  const args = process.argv.slice(2);

  if (args.length === 0 || args.includes('--help') || args.includes('-h')) {
    console.log('n8n Template Search CLI\n');
    console.log('Usage:');
    console.log('  node scripts/find-template.js "search query"');
    console.log('  node scripts/find-template.js --category <category-name>');
    console.log('  node scripts/find-template.js --interactive');
    console.log('  node scripts/find-template.js --list-categories');
    console.log('\nExamples:');
    console.log('  node scripts/find-template.js "video automation"');
    console.log('  node scripts/find-template.js --category ai-video');
    return;
  }

  const index = loadIndex();

  // List categories
  if (args.includes('--list-categories')) {
    console.log('📁 Available Categories:\n');
    index.categories.forEach(c => {
      console.log(`${c.name.padEnd(25)} ${c.templateCount.toString().padStart(3)} templates`);
      console.log(`   ${c.description}`);
      console.log(`   Tags: ${c.tags.join(', ')}`);
      console.log();
    });
    return;
  }

  // Interactive mode
  if (args.includes('--interactive') || args.includes('-i')) {
    await interactiveSearch(index);
    return;
  }

  // Category search
  const categoryIndex = args.indexOf('--category');
  if (categoryIndex !== -1 && args[categoryIndex + 1]) {
    const results = searchByCategory(index, args[categoryIndex + 1]);
    displayResults(results, 20);
    return;
  }

  // Query search
  const query = args.join(' ').replace(/^--(category|interactive)\s*/, '').trim();
  if (query) {
    const results = searchTemplates(index, query);
    displayResults(results, 15);

    if (results.length > 0) {
      console.log('\n💡 Tip: Use --category to browse by category');
    }
  }
}

// Run if called directly
if (require.main === module) {
  main().catch(error => {
    console.error('❌ Error:', error.message);
    process.exit(1);
  });
}

module.exports = { searchTemplates, searchByCategory };
