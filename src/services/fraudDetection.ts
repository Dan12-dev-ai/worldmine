export interface LoginAttempt {
  id: string;
  userId: string;
  timestamp: string;
  ipAddress: string;
  userAgent: string;
  location?: {
    country: string;
    city: string;
  };
  success: boolean;
  riskScore: number;
}

export interface SecurityAlert {
  id: string;
  userId: string;
  type: 'new_location' | 'suspicious_activity' | 'multiple_failures' | 'anomaly';
  severity: 'low' | 'medium' | 'high';
  message: string;
  timestamp: string;
  requires2FA: boolean;
}

export class FraudDetectionService {
  private static instance: FraudDetectionService;
  private readonly MAX_LOGIN_ATTEMPTS = 5;
  private readonly LOCKOUT_DURATION = 15 * 60 * 1000; // 15 minutes
  private readonly RISK_THRESHOLD = 0.7;

  static getInstance(): FraudDetectionService {
    if (!FraudDetectionService.instance) {
      FraudDetectionService.instance = new FraudDetectionService();
    }
    return FraudDetectionService.instance;
  }

  async analyzeLoginAttempt(userId: string, ipAddress: string, userAgent: string): Promise<{
    riskScore: number;
    alerts: SecurityAlert[];
    requires2FA: boolean;
  }> {
    const loginAttempt: LoginAttempt = {
      id: this.generateId(),
      userId,
      timestamp: new Date().toISOString(),
      ipAddress,
      userAgent,
      success: true,
      riskScore: 0
    };

    const location = await this.getLocationFromIP(ipAddress);
    if (location) {
      loginAttempt.location = location;
    }

    const riskScore = await this.calculateRiskScore(loginAttempt);
    loginAttempt.riskScore = riskScore;

    const alerts = await this.generateAlerts(loginAttempt);
    const requires2FA = riskScore > this.RISK_THRESHOLD || alerts.some(alert => alert.requires2FA);

    await this.storeLoginAttempt(loginAttempt);
    await this.storeAlerts(alerts);

    return {
      riskScore,
      alerts,
      requires2FA
    };
  }

  private async calculateRiskScore(attempt: LoginAttempt): Promise<number> {
    let riskScore = 0;

    const previousAttempts = this.getPreviousAttempts(attempt.userId);
    const recentAttempts = previousAttempts.filter(
      a => new Date(a.timestamp).getTime() > Date.now() - 24 * 60 * 60 * 1000
    );

    if (recentAttempts.length === 0) {
      riskScore += 0.1; // New user
    }

    const uniqueIPs = new Set(recentAttempts.map(a => a.ipAddress));
    if (uniqueIPs.size > 3) {
      riskScore += 0.3;
    }

    if (attempt.location) {
      const previousLocations = recentAttempts
        .filter(a => a.location)
        .map(a => a.location!.country);
      
      if (!previousLocations.includes(attempt.location.country)) {
        riskScore += 0.4;
      }
    }

    const failedAttempts = recentAttempts.filter(a => !a.success).length;
    if (failedAttempts > 2) {
      riskScore += 0.3;
    }

    const userAgentHash = this.hashUserAgent(attempt.userAgent);
    const previousUserAgents = recentAttempts.map(a => this.hashUserAgent(a.userAgent));
    if (!previousUserAgents.includes(userAgentHash)) {
      riskScore += 0.2;
    }

    return Math.min(riskScore, 1);
  }

  private async generateAlerts(attempt: LoginAttempt): Promise<SecurityAlert[]> {
    const alerts: SecurityAlert[] = [];

    if (attempt.location) {
      const previousLocations = this.getPreviousAttempts(attempt.userId)
        .filter(a => a.location)
        .map(a => a.location!.country);

      if (!previousLocations.includes(attempt.location.country)) {
        alerts.push({
          id: this.generateId(),
          userId: attempt.userId,
          type: 'new_location',
          severity: 'medium',
          message: `New login detected from ${attempt.location.country}`,
          timestamp: attempt.timestamp,
          requires2FA: true
        });
      }
    }

    const recentFailures = this.getPreviousAttempts(attempt.userId)
      .filter(a => !a.success && new Date(a.timestamp).getTime() > Date.now() - 60 * 60 * 1000)
      .length;

    if (recentFailures >= this.MAX_LOGIN_ATTEMPTS) {
      alerts.push({
        id: this.generateId(),
        userId: attempt.userId,
        type: 'multiple_failures',
        severity: 'high',
        message: 'Multiple failed login attempts detected',
        timestamp: attempt.timestamp,
        requires2FA: true
      });
    }

    if (attempt.riskScore > 0.8) {
      alerts.push({
        id: this.generateId(),
        userId: attempt.userId,
        type: 'anomaly',
        severity: 'high',
        message: 'Suspicious login activity detected',
        timestamp: attempt.timestamp,
        requires2FA: true
      });
    }

    return alerts;
  }

  private async getLocationFromIP(ipAddress: string): Promise<{ country: string; city: string } | null> {
    try {
      const response = await fetch(`https://ipapi.co/${ipAddress}/json/`);
      const data = await response.json();
      
      if (data.country_name && data.city) {
        return {
          country: data.country_name,
          city: data.city
        };
      }
    } catch (error) {
      console.error('Failed to get location from IP:', error);
    }
    
    return null;
  }

  private hashUserAgent(userAgent: string): string {
    let hash = 0;
    for (let i = 0; i < userAgent.length; i++) {
      const char = userAgent.charCodeAt(i);
      hash = ((hash << 5) - hash) + char;
      hash = hash & hash;
    }
    return hash.toString(36);
  }

  private getPreviousAttempts(userId: string): LoginAttempt[] {
    try {
      const stored = localStorage.getItem(`login_attempts_${userId}`);
      return stored ? JSON.parse(stored) : [];
    } catch {
      return [];
    }
  }

  private async storeLoginAttempt(attempt: LoginAttempt): Promise<void> {
    try {
      const attempts = this.getPreviousAttempts(attempt.userId);
      attempts.push(attempt);
      
      const filtered = attempts.filter(
        a => new Date(a.timestamp).getTime() > Date.now() - 7 * 24 * 60 * 60 * 1000
      );
      
      localStorage.setItem(`login_attempts_${attempt.userId}`, JSON.stringify(filtered));
    } catch (error) {
      console.error('Failed to store login attempt:', error);
    }
  }

  private async storeAlerts(alerts: SecurityAlert[]): Promise<void> {
    try {
      alerts.forEach(alert => {
        const existingAlerts = this.getAlerts(alert.userId);
        existingAlerts.push(alert);
        
        const filtered = existingAlerts.filter(
          a => new Date(a.timestamp).getTime() > Date.now() - 7 * 24 * 60 * 60 * 1000
        );
        
        localStorage.setItem(`security_alerts_${alert.userId}`, JSON.stringify(filtered));
      });
    } catch (error) {
      console.error('Failed to store alerts:', error);
    }
  }

  getAlerts(userId: string): SecurityAlert[] {
    try {
      const stored = localStorage.getItem(`security_alerts_${userId}`);
      return stored ? JSON.parse(stored) : [];
    } catch {
      return [];
    }
  }

  async dismissAlert(userId: string, alertId: string): Promise<boolean> {
    try {
      const alerts = this.getAlerts(userId);
      const filtered = alerts.filter(a => a.id !== alertId);
      localStorage.setItem(`security_alerts_${userId}`, JSON.stringify(filtered));
      return true;
    } catch {
      return false;
    }
  }

  private generateId(): string {
    return Date.now().toString(36) + Math.random().toString(36).substring(2);
  }
}

export const fraudDetection = FraudDetectionService.getInstance();
