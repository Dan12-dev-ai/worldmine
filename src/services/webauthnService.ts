export interface WebAuthnCredentialCreationOptions {
  username: string;
  displayName: string;
  userId: string;
}

export interface WebAuthnCredentialRequestOptions {
  username?: string;
}

export class WebAuthnService {
  private static instance: WebAuthnService;
  private rpName = 'Worldmine Marketplace';
  private rpId = window.location.hostname;
  private rpOrigin = window.location.origin;

  static getInstance(): WebAuthnService {
    if (!WebAuthnService.instance) {
      WebAuthnService.instance = new WebAuthnService();
    }
    return WebAuthnService.instance;
  }

  async isSupported(): Promise<boolean> {
    return !!(navigator.credentials && navigator.credentials.create && navigator.credentials.get && window.PublicKeyCredential);
  }

  async createPasskey(options: WebAuthnCredentialCreationOptions): Promise<boolean> {
    try {
      if (!(await this.isSupported())) {
        throw new Error('WebAuthn is not supported on this device');
      }

      const credentialCreationOptions: CredentialCreationOptions = {
        publicKey: {
          challenge: this.generateChallenge(),
          rp: {
            name: this.rpName,
            id: this.rpId,
          },
          user: {
            id: new TextEncoder().encode(options.userId),
            name: options.username,
            displayName: options.displayName,
          },
          pubKeyCredParams: [
            { alg: -7, type: 'public-key' },
            { alg: -257, type: 'public-key' },
          ],
          authenticatorSelection: {
            authenticatorAttachment: 'platform',
            userVerification: 'required',
            residentKey: 'preferred',
          },
          timeout: 60000,
          attestation: 'direct',
        },
      };

      const credential = await navigator.credentials.create(credentialCreationOptions) as PublicKeyCredential;
      
      if (credential) {
        await this.storeCredential(credential, options);
        return true;
      }

      return false;
    } catch (error) {
      console.error('Passkey creation failed:', error);
      throw new Error('Failed to create passkey');
    }
  }

  async authenticateWithPasskey(options?: WebAuthnCredentialRequestOptions): Promise<boolean> {
    try {
      if (!this.isSupported()) {
        throw new Error('WebAuthn is not supported on this device');
      }

      const storedCredentials = this.getStoredCredentials();
      if (storedCredentials.length === 0) {
        throw new Error('No passkeys found');
      }

      const allowCredentials = options?.username
        ? storedCredentials
            .filter(cred => cred.username === options.username)
            .map(cred => ({
              id: this.base64ToArrayBuffer(cred.id),
              type: 'public-key' as const,
              transports: cred.transports || [],
            }))
        : storedCredentials.map(cred => ({
            id: this.base64ToArrayBuffer(cred.id),
            type: 'public-key' as const,
            transports: cred.transports || [],
          }));

      const credentialRequestOptions: CredentialRequestOptions = {
        publicKey: {
          challenge: this.generateChallenge(),
          allowCredentials,
          userVerification: 'required',
          timeout: 60000,
        },
      };

      const credential = await navigator.credentials.get(credentialRequestOptions);
      
      return credential !== null;
    } catch (error) {
      console.error('Passkey authentication failed:', error);
      throw new Error('Failed to authenticate with passkey');
    }
  }

  async authenticateWithBiometric(): Promise<boolean> {
    try {
      if (!(await this.isSupported())) {
        throw new Error('Biometric authentication not supported');
      }

      const credentialRequestOptions: CredentialRequestOptions = {
        publicKey: {
          challenge: this.generateChallenge(),
          allowCredentials: [],
          userVerification: 'required',
          timeout: 60000,
        },
      };

      const credential = await navigator.credentials.get(credentialRequestOptions);
      
      return credential !== null;
    } catch (error) {
      console.error('Biometric authentication failed:', error);
      throw new Error('Biometric authentication failed');
    }
  }

  private generateChallenge(): ArrayBuffer {
    const array = new Uint8Array(32);
    crypto.getRandomValues(array);
    return array.buffer as ArrayBuffer;
  }

  private arrayBufferToBase64(buffer: ArrayBuffer): string {
    const bytes = new Uint8Array(buffer);
    let binary = '';
    for (let i = 0; i < bytes.byteLength; i++) {
      binary += String.fromCharCode(bytes[i]);
    }
    return btoa(binary).replace(/\+/g, '-').replace(/\//g, '_').replace(/=/g, '');
  }

  private base64ToArrayBuffer(base64: string): ArrayBuffer {
    const base64Url = base64.replace(/-/g, '+').replace(/_/g, '/');
    const padded = base64Url.padEnd(base64Url.length + (4 - base64Url.length % 4) % 4, '=');
    const binary = atob(padded);
    const bytes = new Uint8Array(binary.length);
    for (let i = 0; i < binary.length; i++) {
      bytes[i] = binary.charCodeAt(i);
    }
    return bytes.buffer;
  }

  private async storeCredential(credential: PublicKeyCredential, options: WebAuthnCredentialCreationOptions): Promise<void> {
    try {
      const response = credential.response as AuthenticatorAttestationResponse;
      const credentialData = {
        id: this.arrayBufferToBase64(credential.rawId),
        type: credential.type,
        username: options.username,
        displayName: options.displayName,
        userId: options.userId,
        publicKey: this.arrayBufferToBase64(response.getPublicKey() || new ArrayBuffer(0)),
        transports: response.getTransports?.() || [],
        createdAt: new Date().toISOString(),
      };

      const existingCredentials = this.getStoredCredentials();
      existingCredentials.push(credentialData);
      localStorage.setItem('webauthn_credentials', JSON.stringify(existingCredentials));
    } catch (error) {
      console.error('Failed to store credential:', error);
      throw error;
    }
  }

  private getStoredCredentials(): any[] {
    try {
      const stored = localStorage.getItem('webauthn_credentials');
      return stored ? JSON.parse(stored) : [];
    } catch {
      return [];
    }
  }

  async hasPasskeys(): Promise<boolean> {
    const credentials = this.getStoredCredentials();
    return credentials.length > 0;
  }

  async removePasskey(credentialId: string): Promise<boolean> {
    try {
      const credentials = this.getStoredCredentials();
      const filtered = credentials.filter(cred => cred.id !== credentialId);
      localStorage.setItem('webauthn_credentials', JSON.stringify(filtered));
      return true;
    } catch {
      return false;
    }
  }

  getPasskeyList(): Array<{ id: string; username: string; displayName: string; createdAt: string }> {
    return this.getStoredCredentials().map(cred => ({
      id: cred.id,
      username: cred.username,
      displayName: cred.displayName,
      createdAt: cred.createdAt,
    }));
  }
}

export const webauthnService = WebAuthnService.getInstance();
