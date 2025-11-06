#!/usr/bin/env node
/**
 * n8n Template Index Builder
 *
 * Searches n8n community templates and builds a structured index
 * for quick reference and integration into workflows.
 *
 * Usage: node scripts/build-template-index.js
 */

const fs = require('fs');
const path = require('path');

// Category definitions with search queries
const CATEGORIES = [
  {
    name: 'ai-video',
    displayName: 'AI Video Automation',
    query: 'AI video automation generation',
    description: 'AI-powered video generation, editing, and publishing workflows',
    tags: ['ai', 'video', 'automation', 'youtube', 'openai']
  },
  {
    name: 'content-creation',
    displayName: 'Content Creation',
    query: 'content creation writing automation',
    description: 'Automated content generation, SEO, and publishing workflows',
    tags: ['content', 'writing', 'seo', 'blog', 'social-media']
  },
  {
    name: 'data-processing',
    displayName: 'Data Processing',
    query: 'data processing transformation ETL',
    description: 'Data extraction, transformation, and loading workflows',
    tags: ['data', 'etl', 'database', 'api', 'processing']
  },
  {
    name: 'social-media',
    displayName: 'Social Media',
    query: 'social media automation posting',
    description: 'Social media management and automation workflows',
    tags: ['social', 'twitter', 'instagram', 'facebook', 'scheduling']
  },
  {
    name: 'business-automation',
    displayName: 'Business Automation',
    query: 'business workflow automation CRM',
    description: 'Business process automation and CRM workflows',
    tags: ['business', 'crm', 'sales', 'automation', 'productivity']
  }
];

/**
 * Mock MCP search_templates function
 * In production, this would call the actual n8n MCP server
 */
async function mockSearchTemplates({ query, limit, fields }) {
  console.log(`  🔍 Searching: "${query}" (limit: ${limit})`);

  // Return empty results for now - will be replaced with actual MCP calls
  return {
    items: [],
    total: 0,
    hasMore: false,
    query
  };
}

/**
 * Build template index from n8n community templates
 */
async function buildTemplateIndex() {
  console.log('📦 Building n8n Template Index\n');
  console.log('=' .repeat(60));

  const index = {
    generated: new Date().toISOString(),
    version: '1.0.0',
    description: 'Searchable index of n8n community templates organized by category',
    categories: [],
    totalTemplates: 0,
    statistics: {
      byCategory: {},
      topNodes: {},
      totalCategories: CATEGORIES.length
    }
  };

  for (const category of CATEGORIES) {
    console.log(`\n📁 Category: ${category.displayName}`);
    console.log('-'.repeat(60));

    try {
      // Search templates for this category
      const results = await mockSearchTemplates({
        query: category.query,
        limit: 20,
        fields: ['id', 'name', 'description', 'nodes', 'views', 'created']
      });

      const templates = results.items.map(t => ({
        id: t.id,
        name: t.name,
        description: t.description ? t.description.substring(0, 250) + '...' : '',
        nodeCount: t.nodes?.length || 0,
        nodes: t.nodes || [],
        popularity: t.views || 0,
        created: t.created,
        relevance: 'high' // Could be calculated based on search score
      }));

      // Update statistics
      index.statistics.byCategory[category.name] = templates.length;

      // Track node usage
      templates.forEach(t => {
        t.nodes.forEach(node => {
          index.statistics.topNodes[node] = (index.statistics.topNodes[node] || 0) + 1;
        });
      });

      index.categories.push({
        name: category.name,
        displayName: category.displayName,
        description: category.description,
        tags: category.tags,
        query: category.query,
        templateCount: templates.length,
        templates
      });

      index.totalTemplates += templates.length;

      console.log(`  ✅ Found ${templates.length} templates`);

    } catch (error) {
      console.error(`  ❌ Error searching category: ${error.message}`);
    }
  }

  console.log('\n' + '='.repeat(60));
  console.log(`✅ Index built: ${index.totalTemplates} templates across ${index.categories.length} categories`);

  return index;
}

/**
 * Save index to file
 */
function saveIndex(index, outputPath) {
  const dir = path.dirname(outputPath);
  if (!fs.existsSync(dir)) {
    fs.mkdirSync(dir, { recursive: true });
  }

  fs.writeFileSync(
    outputPath,
    JSON.stringify(index, null, 2),
    'utf-8'
  );

  console.log(`\n💾 Index saved to: ${outputPath}`);
  console.log(`   File size: ${(fs.statSync(outputPath).size / 1024).toFixed(2)} KB`);
}

/**
 * Generate summary statistics
 */
function generateStats(index) {
  console.log('\n📊 Statistics');
  console.log('-'.repeat(60));
  console.log(`Total templates: ${index.totalTemplates}`);
  console.log(`Categories: ${index.statistics.totalCategories}`);

  console.log('\n📁 By Category:');
  Object.entries(index.statistics.byCategory)
    .sort((a, b) => b[1] - a[1])
    .forEach(([cat, count]) => {
      console.log(`  ${cat.padEnd(20)} ${count.toString().padStart(3)} templates`);
    });

  console.log('\n🔧 Top 10 Nodes:');
  Object.entries(index.statistics.topNodes)
    .sort((a, b) => b[1] - a[1])
    .slice(0, 10)
    .forEach(([node, count]) => {
      const shortName = node.replace('n8n-nodes-base.', '').replace('@n8n/n8n-nodes-langchain.', 'lc:');
      console.log(`  ${shortName.padEnd(30)} ${count.toString().padStart(3)} uses`);
    });
}

/**
 * Main execution
 */
async function main() {
  try {
    const index = await buildTemplateIndex();

    const outputPath = path.join(__dirname, '..', 'templates', '00-index.json');
    saveIndex(index, outputPath);

    generateStats(index);

    console.log('\n🎯 Next steps:');
    console.log('  1. Review templates/00-index.json');
    console.log('  2. Run: node scripts/find-template.js "your query"');
    console.log('  3. Download specific templates with: node scripts/download-template.js <id>');

  } catch (error) {
    console.error('\n❌ Error building index:', error.message);
    console.error(error.stack);
    process.exit(1);
  }
}

// Run if called directly
if (require.main === module) {
  main();
}

module.exports = { buildTemplateIndex, CATEGORIES };
