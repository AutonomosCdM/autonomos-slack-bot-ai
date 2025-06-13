const { Octokit } = require('@octokit/rest');
const logger = require('../utils/logger').createModuleLogger('GitHubMCP');
const mcpConfig = require('../config/mcpConfig');

/**
 * GitHub MCP - Repository management and interaction
 * Provides comprehensive GitHub API integration for code management
 */
class GitHubMCP {
    constructor() {
        this.config = mcpConfig.getMCPConfig('github');
        this.octokit = null;
        this.authenticated = false;
        this.rateLimitInfo = null;
    }

    /**
     * Initialize GitHub client with authentication
     * @returns {Promise<boolean>} Success status
     */
    async initialize() {
        try {
            logger.info('Initializing GitHub client...');

            if (!this.config.token) {
                logger.warn('No GitHub token provided - using unauthenticated client with rate limits');
                this.octokit = new Octokit({
                    baseUrl: this.config.baseUrl,
                    request: {
                        timeout: this.config.timeout
                    }
                });
            } else {
                this.octokit = new Octokit({
                    auth: this.config.token,
                    baseUrl: this.config.baseUrl,
                    request: {
                        timeout: this.config.timeout
                    }
                });
                this.authenticated = true;
            }

            // Test authentication and get rate limit info
            await this._updateRateLimitInfo();

            logger.info('GitHub client initialized successfully', {
                authenticated: this.authenticated,
                rateLimit: this.rateLimitInfo
            });

            return true;

        } catch (error) {
            logger.error(`Failed to initialize GitHub client: ${error.message}`);
            throw new Error(`GitHub initialization failed: ${error.message}`);
        }
    }

    /**
     * Search for repositories
     * @param {string} query - Search query
     * @param {Object} options - Search options
     * @returns {Promise<Object>} Search results
     */
    async searchRepositories(query, options = {}) {
        await this._ensureInitialized();
        const startTime = Date.now();

        try {
            logger.info(`Searching repositories: "${query}"`, options);

            const searchParams = {
                q: query,
                sort: options.sort || 'stars',
                order: options.order || 'desc',
                per_page: Math.min(options.limit || 10, 100),
                page: options.page || 1
            };

            const response = await this.octokit.rest.search.repos(searchParams);

            const result = {
                totalCount: response.data.total_count,
                repositories: response.data.items.map(repo => this._formatRepository(repo)),
                searchTime: Date.now() - startTime,
                page: searchParams.page,
                perPage: searchParams.per_page
            };

            logger.info(`Found ${result.totalCount} repositories`, {
                returned: result.repositories.length,
                duration: result.searchTime
            });

            return result;

        } catch (error) {
            logger.error(`Error searching repositories: ${error.message}`, { query });
            throw new Error(`Repository search failed: ${error.message}`);
        }
    }

    /**
     * Get detailed repository information
     * @param {string} owner - Repository owner
     * @param {string} repo - Repository name
     * @returns {Promise<Object>} Repository details
     */
    async getRepository(owner, repo) {
        await this._ensureInitialized();

        try {
            logger.info(`Fetching repository: ${owner}/${repo}`);

            const [repoResponse, contentsResponse] = await Promise.all([
                this.octokit.rest.repos.get({ owner, repo }),
                this.octokit.rest.repos.getContent({ 
                    owner, 
                    repo, 
                    path: '' 
                }).catch(() => ({ data: [] })) // Handle private repos
            ]);

            const repository = this._formatRepository(repoResponse.data, true);
            
            // Add root directory contents
            if (Array.isArray(contentsResponse.data)) {
                repository.rootContents = contentsResponse.data.map(item => ({
                    name: item.name,
                    type: item.type,
                    size: item.size,
                    path: item.path
                }));
            }

            logger.info(`Retrieved repository details for ${owner}/${repo}`);
            return repository;

        } catch (error) {
            logger.error(`Error fetching repository: ${error.message}`, { owner, repo });
            throw new Error(`Repository fetch failed: ${error.message}`);
        }
    }

    /**
     * Get repository file content
     * @param {string} owner - Repository owner
     * @param {string} repo - Repository name
     * @param {string} path - File path
     * @param {string} ref - Branch/commit reference (optional)
     * @returns {Promise<Object>} File content and metadata
     */
    async getFileContent(owner, repo, path, ref = null) {
        await this._ensureInitialized();

        try {
            logger.info(`Fetching file: ${owner}/${repo}/${path}`, { ref });

            const params = { owner, repo, path };
            if (ref) params.ref = ref;

            const response = await this.octokit.rest.repos.getContent(params);
            const file = response.data;

            // Decode content if it's a file
            let content = null;
            if (file.type === 'file' && file.content) {
                content = Buffer.from(file.content, 'base64').toString('utf-8');
            }

            const result = {
                name: file.name,
                path: file.path,
                type: file.type,
                size: file.size,
                content: content,
                sha: file.sha,
                downloadUrl: file.download_url,
                encoding: file.encoding
            };

            logger.info(`Retrieved file content for ${path}`, {
                size: file.size,
                type: file.type
            });

            return result;

        } catch (error) {
            logger.error(`Error fetching file content: ${error.message}`, {
                owner, repo, path, ref
            });
            throw new Error(`File content fetch failed: ${error.message}`);
        }
    }

    /**
     * Get repository branches
     * @param {string} owner - Repository owner
     * @param {string} repo - Repository name
     * @param {number} limit - Maximum number of branches to return
     * @returns {Promise<Array>} List of branches
     */
    async getBranches(owner, repo, limit = 30) {
        await this._ensureInitialized();

        try {
            logger.info(`Fetching branches for ${owner}/${repo}`);

            const response = await this.octokit.rest.repos.listBranches({
                owner,
                repo,
                per_page: Math.min(limit, 100)
            });

            const branches = response.data.map(branch => ({
                name: branch.name,
                sha: branch.commit.sha,
                protected: branch.protected
            }));

            logger.info(`Retrieved ${branches.length} branches for ${owner}/${repo}`);
            return branches;

        } catch (error) {
            logger.error(`Error fetching branches: ${error.message}`, { owner, repo });
            throw new Error(`Branches fetch failed: ${error.message}`);
        }
    }

    /**
     * Get repository commits
     * @param {string} owner - Repository owner
     * @param {string} repo - Repository name
     * @param {Object} options - Query options
     * @returns {Promise<Array>} List of commits
     */
    async getCommits(owner, repo, options = {}) {
        await this._ensureInitialized();

        try {
            logger.info(`Fetching commits for ${owner}/${repo}`, options);

            const params = {
                owner,
                repo,
                per_page: Math.min(options.limit || 10, 100),
                page: options.page || 1
            };

            if (options.branch) params.sha = options.branch;
            if (options.since) params.since = options.since;
            if (options.until) params.until = options.until;
            if (options.path) params.path = options.path;

            const response = await this.octokit.rest.repos.listCommits(params);

            const commits = response.data.map(commit => ({
                sha: commit.sha,
                message: commit.commit.message,
                author: {
                    name: commit.commit.author.name,
                    email: commit.commit.author.email,
                    date: commit.commit.author.date
                },
                committer: {
                    name: commit.commit.committer.name,
                    email: commit.commit.committer.email,
                    date: commit.commit.committer.date
                },
                url: commit.html_url,
                stats: commit.stats
            }));

            logger.info(`Retrieved ${commits.length} commits for ${owner}/${repo}`);
            return commits;

        } catch (error) {
            logger.error(`Error fetching commits: ${error.message}`, { owner, repo });
            throw new Error(`Commits fetch failed: ${error.message}`);
        }
    }

    /**
     * Get repository issues
     * @param {string} owner - Repository owner
     * @param {string} repo - Repository name
     * @param {Object} options - Query options
     * @returns {Promise<Array>} List of issues
     */
    async getIssues(owner, repo, options = {}) {
        await this._ensureInitialized();

        try {
            logger.info(`Fetching issues for ${owner}/${repo}`, options);

            const params = {
                owner,
                repo,
                state: options.state || 'open',
                sort: options.sort || 'created',
                direction: options.direction || 'desc',
                per_page: Math.min(options.limit || 10, 100),
                page: options.page || 1
            };

            if (options.labels) params.labels = options.labels;
            if (options.assignee) params.assignee = options.assignee;
            if (options.milestone) params.milestone = options.milestone;

            const response = await this.octokit.rest.issues.listForRepo(params);

            const issues = response.data
                .filter(issue => !issue.pull_request) // Filter out PRs
                .map(issue => ({
                    id: issue.id,
                    number: issue.number,
                    title: issue.title,
                    body: issue.body,
                    state: issue.state,
                    author: issue.user.login,
                    assignees: issue.assignees.map(a => a.login),
                    labels: issue.labels.map(l => ({ name: l.name, color: l.color })),
                    createdAt: issue.created_at,
                    updatedAt: issue.updated_at,
                    closedAt: issue.closed_at,
                    url: issue.html_url,
                    comments: issue.comments
                }));

            logger.info(`Retrieved ${issues.length} issues for ${owner}/${repo}`);
            return issues;

        } catch (error) {
            logger.error(`Error fetching issues: ${error.message}`, { owner, repo });
            throw new Error(`Issues fetch failed: ${error.message}`);
        }
    }

    /**
     * Get user/organization information
     * @param {string} username - GitHub username or organization
     * @returns {Promise<Object>} User/organization details
     */
    async getUser(username) {
        await this._ensureInitialized();

        try {
            logger.info(`Fetching user: ${username}`);

            const response = await this.octokit.rest.users.getByUsername({
                username
            });

            const user = {
                id: response.data.id,
                login: response.data.login,
                name: response.data.name,
                company: response.data.company,
                blog: response.data.blog,
                location: response.data.location,
                email: response.data.email,
                bio: response.data.bio,
                type: response.data.type,
                publicRepos: response.data.public_repos,
                publicGists: response.data.public_gists,
                followers: response.data.followers,
                following: response.data.following,
                createdAt: response.data.created_at,
                updatedAt: response.data.updated_at,
                avatarUrl: response.data.avatar_url,
                url: response.data.html_url
            };

            logger.info(`Retrieved user information for ${username}`);
            return user;

        } catch (error) {
            logger.error(`Error fetching user: ${error.message}`, { username });
            throw new Error(`User fetch failed: ${error.message}`);
        }
    }

    /**
     * Get current rate limit status
     * @returns {Promise<Object>} Rate limit information
     */
    async getRateLimit() {
        await this._ensureInitialized();

        try {
            const response = await this.octokit.rest.rateLimit.get();
            this.rateLimitInfo = response.data.rate;
            
            logger.debug('Rate limit updated', this.rateLimitInfo);
            return this.rateLimitInfo;

        } catch (error) {
            logger.error(`Error fetching rate limit: ${error.message}`);
            throw new Error(`Rate limit fetch failed: ${error.message}`);
        }
    }

    /**
     * Format repository data for consistent output
     * @private
     */
    _formatRepository(repo, detailed = false) {
        const formatted = {
            id: repo.id,
            name: repo.name,
            fullName: repo.full_name,
            owner: {
                login: repo.owner.login,
                type: repo.owner.type,
                avatarUrl: repo.owner.avatar_url
            },
            description: repo.description,
            language: repo.language,
            languages: repo.languages_url,
            stars: repo.stargazers_count,
            forks: repo.forks_count,
            watchers: repo.watchers_count,
            openIssues: repo.open_issues_count,
            size: repo.size,
            defaultBranch: repo.default_branch,
            private: repo.private,
            archived: repo.archived,
            disabled: repo.disabled,
            createdAt: repo.created_at,
            updatedAt: repo.updated_at,
            pushedAt: repo.pushed_at,
            url: repo.html_url,
            cloneUrl: repo.clone_url,
            topics: repo.topics || []
        };

        if (detailed) {
            formatted.license = repo.license ? {
                name: repo.license.name,
                spdxId: repo.license.spdx_id
            } : null;
            formatted.hasWiki = repo.has_wiki;
            formatted.hasPages = repo.has_pages;
            formatted.hasProjects = repo.has_projects;
            formatted.hasDownloads = repo.has_downloads;
            formatted.networkCount = repo.network_count;
            formatted.subscribersCount = repo.subscribers_count;
        }

        return formatted;
    }

    /**
     * Ensure client is initialized
     * @private
     */
    async _ensureInitialized() {
        if (!this.octokit) {
            await this.initialize();
        }
    }

    /**
     * Update rate limit information
     * @private
     */
    async _updateRateLimitInfo() {
        try {
            const response = await this.octokit.rest.rateLimit.get();
            this.rateLimitInfo = response.data.rate;
        } catch (error) {
            logger.warn(`Could not fetch rate limit info: ${error.message}`);
            this.rateLimitInfo = null;
        }
    }

    /**
     * Get GitHub client status
     * @returns {Object} Client status information
     */
    getStatus() {
        return {
            initialized: !!this.octokit,
            authenticated: this.authenticated,
            rateLimit: this.rateLimitInfo,
            hasToken: !!this.config.token
        };
    }
}

module.exports = GitHubMCP;