// Semantic Versioning (SemVer) Implementation
// ISO/IEC 25010 - Maintainability & Portability Compliance
// Follows SemVer 2.0.0 specification

export interface SemVer {
  major: number;
  minor: number;
  patch: number;
  preRelease?: string;
  buildMetadata?: string;
}

export interface VersionInfo {
  version: SemVer;
  timestamp: string;
  changes: {
    added: string[];
    changed: string[];
    deprecated: string[];
    removed: string[];
    fixed: string[];
    security: string[];
  };
  buildNumber?: number;
  commitHash?: string;
  branch?: string;
}

export interface ChangelogEntry {
  version: SemVer;
  date: string;
  changes: {
    added: string[];
    changed: string[];
    deprecated: string[];
    removed: string[];
    fixed: string[];
    security: string[];
  };
  metadata?: {
    buildNumber?: number;
    commitHash?: string;
    branch?: string;
    author?: string;
    releaseNotes?: string;
  };
}

export class SemanticVersioning {
  private static readonly VERSION_REGEX = /^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)(?:-((?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*)(?:\.(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*))*))?(?:\+([0-9a-zA-Z-]+(?:\.[0-9a-zA-Z-]+)*))?$/;

  /**
   * Parse a version string into SemVer object
   */
  static parse(version: string): SemVer {
    const match = version.match(this.VERSION_REGEX);
    if (!match) {
      throw new Error(`Invalid semantic version: ${version}`);
    }

    return {
      major: parseInt(match[1], 10),
      minor: parseInt(match[2], 10),
      patch: parseInt(match[3], 10),
      preRelease: match[4] || undefined,
      buildMetadata: match[5] || undefined
    };
  }

  /**
   * Convert SemVer object to string
   */
  static stringify(version: SemVer): string {
    let result = `${version.major}.${version.minor}.${version.patch}`;
    
    if (version.preRelease) {
      result += `-${version.preRelease}`;
    }
    
    if (version.buildMetadata) {
      result += `+${version.buildMetadata}`;
    }
    
    return result;
  }

  /**
   * Compare two versions
   * Returns: -1 if a < b, 0 if a === b, 1 if a > b
   */
  static compare(a: SemVer, b: SemVer): number {
    // Compare major version
    if (a.major !== b.major) {
      return a.major < b.major ? -1 : 1;
    }

    // Compare minor version
    if (a.minor !== b.minor) {
      return a.minor < b.minor ? -1 : 1;
    }

    // Compare patch version
    if (a.patch !== b.patch) {
      return a.patch < b.patch ? -1 : 1;
    }

    // Compare pre-release
    if (a.preRelease && b.preRelease) {
      return this.comparePreRelease(a.preRelease, b.preRelease);
    }

    // Versions with pre-release are lower than those without
    if (a.preRelease && !b.preRelease) {
      return -1;
    }
    if (!a.preRelease && b.preRelease) {
      return 1;
    }

    return 0;
  }

  /**
   * Compare pre-release identifiers
   */
  private static comparePreRelease(a: string, b: string): number {
    const aParts = a.split('.');
    const bParts = b.split('.');
    const maxLength = Math.max(aParts.length, bParts.length);

    for (let i = 0; i < maxLength; i++) {
      const aPart = aParts[i];
      const bPart = bParts[i];

      // Missing parts are considered lower
      if (aPart === undefined) return -1;
      if (bPart === undefined) return 1;

      // Numeric identifiers have lower precedence than alphanumeric
      const aIsNumeric = /^\d+$/.test(aPart);
      const bIsNumeric = /^\d+$/.test(bPart);

      if (aIsNumeric && bIsNumeric) {
        const aNum = parseInt(aPart, 10);
        const bNum = parseInt(bPart, 10);
        if (aNum !== bNum) {
          return aNum < bNum ? -1 : 1;
        }
      } else if (aIsNumeric) {
        return -1;
      } else if (bIsNumeric) {
        return 1;
      } else {
        // Alphanumeric comparison
        if (aPart !== bPart) {
          return aPart < bPart ? -1 : 1;
        }
      }
    }

    return 0;
  }

  /**
   * Check if version satisfies constraint
   */
  static satisfies(version: SemVer, constraint: string): boolean {
    // Handle simple version comparison
    if (!constraint.includes(' ')) {
      const constraintVersion = this.parse(constraint);
      return this.compare(version, constraintVersion) >= 0;
    }

    // Handle complex constraints (e.g., "^1.0.0", "~1.0.0", ">=1.0.0 <2.0.0")
    return this.evaluateComplexConstraint(version, constraint);
  }

  /**
   * Evaluate complex version constraints
   */
  private static evaluateComplexConstraint(version: SemVer, constraint: string): boolean {
    // Handle caret (^) constraint
    if (constraint.startsWith('^')) {
      const baseVersion = this.parse(constraint.substring(1));
      return this.satisfiesCaret(version, baseVersion);
    }

    // Handle tilde (~) constraint
    if (constraint.startsWith('~')) {
      const baseVersion = this.parse(constraint.substring(1));
      return this.satisfiesTilde(version, baseVersion);
    }

    // Handle range constraints
    if (constraint.includes(' ')) {
      return this.evaluateRangeConstraint(version, constraint);
    }

    // Handle simple comparison
    const operators = ['>=', '<=', '>', '<', '='];
    for (const op of operators) {
      if (constraint.startsWith(op)) {
        const targetVersion = this.parse(constraint.substring(op.length));
        return this.compareWithOperator(version, targetVersion, op);
      }
    }

    // Default to exact match
    const targetVersion = this.parse(constraint);
    return this.compare(version, targetVersion) === 0;
  }

  /**
   * Evaluate caret (^) constraint
   */
  private static satisfiesCaret(version: SemVer, base: SemVer): boolean {
    // ^1.0.0 allows >=1.0.0 and <2.0.0
    // ^0.1.0 allows >=0.1.0 and <0.2.0
    // ^0.0.1 allows >=0.0.1 and <0.1.0

    if (base.major > 0) {
      // Major version > 0: allow changes in minor and patch
      const min = { ...base };
      const max = { major: base.major + 1, minor: 0, patch: 0 };
      return this.compare(version, min) >= 0 && this.compare(version, max) < 0;
    } else if (base.minor > 0) {
      // Major version = 0, minor > 0: allow changes in patch only
      const min = { ...base };
      const max = { major: 0, minor: base.minor + 1, patch: 0 };
      return this.compare(version, min) >= 0 && this.compare(version, max) < 0;
    } else {
      // Major version = 0, minor = 0: allow no changes
      return this.compare(version, base) >= 0 && this.compare(version, { major: 0, minor: 0, patch: base.patch + 1 }) < 0;
    }
  }

  /**
   * Evaluate tilde (~) constraint
   */
  private static satisfiesTilde(version: SemVer, base: SemVer): boolean {
    // ~1.0.0 allows >=1.0.0 and <1.1.0
    // ~0.1.0 allows >=0.1.0 and <0.2.0

    const min = { ...base };
    const max = base.patch > 0 
      ? { ...base, patch: base.patch + 1 }
      : { major: base.major, minor: base.minor + 1, patch: 0 };

    return this.compare(version, min) >= 0 && this.compare(version, max) < 0;
  }

  /**
   * Evaluate range constraint
   */
  private static evaluateRangeConstraint(version: SemVer, constraint: string): boolean {
    // Handle ">=1.0.0 <2.0.0" format
    const parts = constraint.split(' ');
    if (parts.length === 2) {
      const leftOp = parts[0];
      const rightOp = parts[1];
      
      const leftVersion = this.parse(leftOp.substring(2));
      const rightVersion = this.parse(rightOp.substring(2));
      
      const leftSatisfied = this.compareWithOperator(version, leftVersion, leftOp.substring(0, 2));
      const rightSatisfied = this.compareWithOperator(version, rightVersion, rightOp.substring(0, 2));
      
      return leftSatisfied && rightSatisfied;
    }

    return false;
  }

  /**
   * Compare version with operator
   */
  private static compareWithOperator(version: SemVer, target: SemVer, operator: string): boolean {
    const comparison = this.compare(version, target);
    switch (operator) {
      case '>=': return comparison >= 0;
      case '<=': return comparison <= 0;
      case '>': return comparison > 0;
      case '<': return comparison < 0;
      case '=': return comparison === 0;
      default: return false;
    }
  }

  /**
   * Increment version
   */
  static increment(version: SemVer, type: 'major' | 'minor' | 'patch'): SemVer {
    const newVersion = { ...version };
    
    switch (type) {
      case 'major':
        newVersion.major += 1;
        newVersion.minor = 0;
        newVersion.patch = 0;
        break;
      case 'minor':
        newVersion.minor += 1;
        newVersion.patch = 0;
        break;
      case 'patch':
        newVersion.patch += 1;
        break;
    }
    
    // Clear pre-release and build metadata for release versions
    newVersion.preRelease = undefined;
    newVersion.buildMetadata = undefined;
    
    return newVersion;
  }

  /**
   * Get the highest version from an array
   */
  static max(versions: SemVer[]): SemVer {
    if (versions.length === 0) {
      throw new Error('Cannot get max of empty array');
    }
    
    return versions.reduce((max, current) => 
      this.compare(current, max) > 0 ? current : max
    );
  }

  /**
   * Get the lowest version from an array
   */
  static min(versions: SemVer[]): SemVer {
    if (versions.length === 0) {
      throw new Error('Cannot get min of empty array');
    }
    
    return versions.reduce((min, current) => 
      this.compare(current, min) < 0 ? current : min
    );
  }

  /**
   * Sort versions in ascending order
   */
  static sort(versions: SemVer[]): SemVer[] {
    return [...versions].sort((a, b) => this.compare(a, b));
  }

  /**
   * Sort versions in descending order
   */
  static sortDescending(versions: SemVer[]): SemVer[] {
    return [...versions].sort((a, b) => this.compare(b, a));
  }

  /**
   * Check if version is a pre-release
   */
  static isPreRelease(version: SemVer): boolean {
    return !!version.preRelease;
  }

  /**
   * Check if version is stable (no pre-release)
   */
  static isStable(version: SemVer): boolean {
    return !version.preRelease;
  }

  /**
   * Get the distance between two versions
   */
  static distance(a: SemVer, b: SemVer): number {
    const majorDiff = Math.abs(a.major - b.major) * 1000000;
    const minorDiff = Math.abs(a.minor - b.minor) * 10000;
    const patchDiff = Math.abs(a.patch - b.patch) * 100;
    
    return majorDiff + minorDiff + patchDiff;
  }

  /**
   * Get next version based on changes
   */
  static getNextVersion(
    current: SemVer,
    changes: {
      added?: string[];
      changed?: string[];
      deprecated?: string[];
      removed?: string[];
      fixed?: string[];
      security?: string[];
    }
  ): SemVer {
    // Breaking changes (removed) -> major version
    if (changes.removed && changes.removed.length > 0) {
      return this.increment(current, 'major');
    }

    // Security fixes -> patch version
    if (changes.security && changes.security.length > 0) {
      return this.increment(current, 'patch');
    }

    // Bug fixes -> patch version
    if (changes.fixed && changes.fixed.length > 0) {
      return this.increment(current, 'patch');
    }

    // New features or changes -> minor version
    if ((changes.added && changes.added.length > 0) || 
        (changes.changed && changes.changed.length > 0)) {
      return this.increment(current, 'minor');
    }

    // Deprecated features -> patch version
    if (changes.deprecated && changes.deprecated.length > 0) {
      return this.increment(current, 'patch');
    }

    // No changes -> same version
    return current;
  }

  /**
   * Generate changelog entry
   */
  static generateChangelogEntry(
    version: SemVer,
    changes: {
      added?: string[];
      changed?: string[];
      deprecated?: string[];
      removed?: string[];
      fixed?: string[];
      security?: string[];
    },
    metadata?: {
      buildNumber?: number;
      commitHash?: string;
      branch?: string;
      author?: string;
      releaseNotes?: string;
    }
  ): ChangelogEntry {
    return {
      version,
      date: new Date().toISOString().split('T')[0],
      changes: {
        added: changes.added || [],
        changed: changes.changed || [],
        deprecated: changes.deprecated || [],
        removed: changes.removed || [],
        fixed: changes.fixed || [],
        security: changes.security || []
      },
      metadata
    };
  }

  /**
   * Format version for display
   */
  static format(version: SemVer, options?: {
    includePreRelease?: boolean;
    includeBuildMetadata?: boolean;
    prefix?: string;
  }): string {
    let result = `${options?.prefix || ''}${version.major}.${version.minor}.${version.patch}`;
    
    if (options?.includePreRelease !== false && version.preRelease) {
      result += `-${version.preRelease}`;
    }
    
    if (options?.includeBuildMetadata !== false && version.buildMetadata) {
      result += `+${version.buildMetadata}`;
    }
    
    return result;
  }

  /**
   * Parse version from package.json
   */
  static fromPackageJson(packageJson: any): SemVer {
    const version = packageJson.version;
    if (!version) {
      throw new Error('Package.json does not contain version field');
    }
    
    return this.parse(version);
  }

  /**
   * Validate version format
   */
  static isValid(version: string): boolean {
    try {
      this.parse(version);
      return true;
    } catch {
      return false;
    }
  }

  /**
   * Get version compatibility matrix
   */
  static getCompatibilityMatrix(current: SemVer, versions: SemVer[]): Array<{
    version: SemVer;
    compatible: boolean;
    reason: string;
  }> {
    return versions.map(v => {
      const comparison = this.compare(v, current);
      
      if (comparison === 0) {
        return { version: v, compatible: true, reason: 'Same version' };
      }
      
      if (v.major === current.major) {
        if (v.minor === current.minor) {
          return { version: v, compatible: true, reason: 'Same major and minor version' };
        } else if (v.minor < current.minor) {
          return { version: v, compatible: true, reason: 'Older minor version (backward compatible)' };
        } else {
          return { version: v, compatible: false, reason: 'Newer minor version (may have breaking changes)' };
        }
      } else if (v.major < current.major) {
        return { version: v, compatible: false, reason: 'Older major version (incompatible)' };
      } else {
        return { version: v, compatible: false, reason: 'Newer major version (breaking changes)' };
      }
    });
  }
}

// Version Manager for application versioning
export class VersionManager {
  private currentVersion: SemVer;
  private changelog: ChangelogEntry[] = [];
  private buildInfo: {
    buildNumber: number;
    commitHash: string;
    branch: string;
    timestamp: string;
  };

  constructor(initialVersion: SemVer) {
    this.currentVersion = initialVersion;
    this.buildInfo = {
      buildNumber: 1,
      commitHash: 'unknown',
      branch: 'main',
      timestamp: new Date().toISOString()
    };
  }

  /**
   * Get current version
   */
  getCurrentVersion(): SemVer {
    return this.currentVersion;
  }

  /**
   * Get formatted current version
   */
  getCurrentVersionString(options?: Parameters<typeof SemanticVersioning.format>[1]): string {
    return SemanticVersioning.format(this.currentVersion, options);
  }

  /**
   * Update version with changes
   */
  updateVersion(changes: {
    added?: string[];
    changed?: string[];
    deprecated?: string[];
    removed?: string[];
    fixed?: string[];
    security?: string[];
  }): SemVer {
    const newVersion = SemanticVersioning.getNextVersion(this.currentVersion, changes);
    
    const entry = SemanticVersioning.generateChangelogEntry(newVersion, changes, {
      buildNumber: this.buildInfo.buildNumber,
      commitHash: this.buildInfo.commitHash,
      branch: this.buildInfo.branch
    });
    
    this.changelog.push(entry);
    this.currentVersion = newVersion;
    this.buildInfo.buildNumber++;
    this.buildInfo.timestamp = new Date().toISOString();
    
    return newVersion;
  }

  /**
   * Get changelog
   */
  getChangelog(): ChangelogEntry[] {
    return [...this.changelog];
  }

  /**
   * Get build info
   */
  getBuildInfo(): typeof this.buildInfo {
    return { ...this.buildInfo };
  }

  /**
   * Set build info
   */
  setBuildInfo(info: Partial<typeof this.buildInfo>): void {
    this.buildInfo = { ...this.buildInfo, ...info };
  }

  /**
   * Check if version is compatible with constraint
   */
  isCompatible(constraint: string): boolean {
    return SemanticVersioning.satisfies(this.currentVersion, constraint);
  }

  /**
   * Get version info
   */
  getVersionInfo(): VersionInfo {
    return {
      version: this.currentVersion,
      timestamp: this.buildInfo.timestamp,
      changes: this.changelog.length > 0 ? this.changelog[this.changelog.length - 1].changes : {
        added: [],
        changed: [],
        deprecated: [],
        removed: [],
        fixed: [],
        security: []
      },
      buildNumber: this.buildInfo.buildNumber,
      commitHash: this.buildInfo.commitHash,
      branch: this.buildInfo.branch
    };
  }

  /**
   * Export version data
   */
  export(): {
    currentVersion: SemVer;
    changelog: ChangelogEntry[];
    buildInfo: typeof this.buildInfo;
  } {
    return {
      currentVersion: this.currentVersion,
      changelog: this.changelog,
      buildInfo: this.buildInfo
    };
  }

  /**
   * Import version data
   */
  import(data: {
    currentVersion: SemVer;
    changelog: ChangelogEntry[];
    buildInfo: typeof this.buildInfo;
  }): void {
    this.currentVersion = data.currentVersion;
    this.changelog = data.changelog;
    this.buildInfo = data.buildInfo;
  }
}

// Default version manager instance
export const versionManager = new VersionManager({
  major: 1,
  minor: 0,
  patch: 1,
  preRelease: 'beta'
});

// Export utilities
export const parseVersion = SemanticVersioning.parse;
export const formatVersion = SemanticVersioning.format;
export const compareVersions = SemanticVersioning.compare;
export const incrementVersion = SemanticVersioning.increment;
export const isValidVersion = SemanticVersioning.isValid;
export const satisfiesConstraint = SemanticVersioning.satisfies;

export default SemanticVersioning;
