/**
 * 🚀 DEDAN 2.0 - AI-Powered Onboarding & KYC System
 * Complete registration in <3 minutes with instant AI verification
 * Mobile-friendly document capture with biometric authentication
 */

import React, { useState, useEffect, useRef, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Camera, Upload, CheckCircle, AlertTriangle,
  User, Shield, Eye, EyeOff, Lock,
  Smartphone, Mail, Globe,
  ChevronRight, ChevronLeft, RefreshCw,
  Fingerprint, UserCheck
} from 'lucide-react';

interface OnboardingStep {
  id: string;
  title: string;
  description: string;
  icon: React.ReactNode;
  required: boolean;
  completed: boolean;
  error?: string;
}

interface DocumentData {
  id: string;
  type: 'passport' | 'id_card' | 'driving_license' | 'proof_of_address';
  name: string;
  file: File | null;
  uploaded: boolean;
  verified: boolean;
  error?: string;
  preview?: string;
}

interface UserData {
  email: string;
  password: string;
  firstName: string;
  lastName: string;
  phone: string;
  dateOfBirth: string;
  nationality: string;
  address: {
    street: string;
    city: string;
    state: string;
    zipCode: string;
    country: string;
  };
  acceptTerms: boolean;
  acceptPrivacy: boolean;;
}

interface KYCResult {
  status: 'pending' | 'processing' | 'approved' | 'rejected';
  riskScore: number;
  verificationId: string;
  estimatedTime: number;
  message?: string;
}

const OnboardingKYC: React.FC = () => {
  // State management
  const [currentStep, setCurrentStep] = useState(0);
  const [userData, setUserData] = useState<UserData>({
    email: '',
    password: '',
    firstName: '',
    lastName: '',
    phone: '',
    dateOfBirth: '',
    nationality: '',
    address: {
      street: '',
      city: '',
      state: '',
      zipCode: '',
      country: ''
    },
    acceptTerms: false,
    acceptPrivacy: false
  });
  
  const [documents, setDocuments] = useState<DocumentData[]>([
    { id: 'passport', type: 'passport', name: 'Passport', file: null, uploaded: false, verified: false },
    { id: 'id_card', type: 'id_card', name: 'ID Card', file: null, uploaded: false, verified: false },
    { id: 'proof_of_address', type: 'proof_of_address', name: 'Proof of Address', file: null, uploaded: false, verified: false }
  ]);
  
  const [kycResult, setKycResult] = useState<KYCResult>({
    status: 'pending',
    riskScore: 0,
    verificationId: '',
    estimatedTime: 120
  });
  
  const [isProcessing, setIsProcessing] = useState(false);
  const [biometricEnabled, setBiometricEnabled] = useState(false);
  const [cameraStream, setCameraStream] = useState<MediaStream | null>(null);
  const [showPassword, setShowPassword] = useState(false);
  const [supportedCountries, setSupportedCountries] = useState<string[]>([]);
  const [faceScanActive, setFaceScanActive] = useState(false);
  const [scanProgress, setScanProgress] = useState(0);
  
  // Refs
  const fileInputRef = useRef<HTMLInputElement>(null);
  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);

  // Onboarding steps
  const steps: OnboardingStep[] = [
    {
      id: 'account',
      title: 'Create Account',
      description: 'Set up your DEDAN 2.0 account with email and password',
      icon: <User className="w-6 h-6" />,
      required: true,
      completed: userData.email && userData.password && userData.acceptTerms && userData.acceptPrivacy
    },
    {
      id: 'personal',
      title: 'Personal Information',
      description: 'Provide your personal details for verification',
      icon: <UserCheck className="w-6 h-6" />,
      required: true,
      completed: userData.firstName && userData.lastName && userData.dateOfBirth && userData.nationality
    },
    {
      id: 'documents',
      title: 'Document Verification',
      description: 'Upload required documents for AI-powered verification',
      icon: <Shield className="w-6 h-6" />,
      required: true,
      completed: documents.filter(doc => doc.uploaded && doc.verified).length >= 2
    },
    {
      id: 'biometric',
      title: 'Biometric Verification',
      description: 'Complete facial recognition for instant verification',
      icon: <Fingerprint className="w-6 h-6" />,
      required: true,
      completed: kycResult.status === 'approved'
    }
  ];

  // Initialize supported countries
  useEffect(() => {
    const countries = [
      'United States', 'United Kingdom', 'Germany', 'France', 'Switzerland',
      'Japan', 'Singapore', 'Australia', 'Canada', 'Netherlands',
      'Sweden', 'Norway', 'Denmark', 'Finland', 'Belgium',
      'Austria', 'Spain', 'Italy', 'Portugal', 'Ireland'
    ];
    setSupportedCountries(countries);
  }, []);

  // Check biometric support
  useEffect(() => {
    const checkBiometricSupport = async () => {
      try {
        // Check if WebAuthn is supported
        if (window.PublicKeyCredential) {
          setBiometricEnabled(true);
        }
      } catch (error) {
        console.log('Biometric authentication not supported');
      }
    };
    
    checkBiometricSupport();
  }, []);

  // Handle file upload with AI processing
  const handleFileUpload = useCallback(async (documentId: string, file: File) => {
    setIsProcessing(true);
    
    try {
      // Simulate AI document processing
      const reader = new FileReader();
      reader.onload = async (e) => {
        const preview = e.target?.result as string;
        
        // Simulate AI validation (tilt detection, blur detection, etc.)
        await new Promise(resolve => setTimeout(resolve, 1500));
        
        const isValid = Math.random() > 0.1; // 90% success rate
        
        setDocuments(prev => prev.map(doc => 
          doc.id === documentId 
            ? {
                ...doc,
                file,
                preview,
                uploaded: true,
                verified: isValid,
                error: isValid ? undefined : 'Document validation failed'
              }
            : doc
        ));
        
        setIsProcessing(false);
      };
      
      reader.readAsDataURL(file);
    } catch (error) {
      setDocuments(prev => prev.map(doc => 
        doc.id === documentId 
          ? { ...doc, error: 'Upload failed' }
          : doc
      ));
      setIsProcessing(false);
    }
  }, []);

  // Start facial recognition scan
  const startFaceScan = useCallback(async () => {
    setFaceScanActive(true);
    setScanProgress(0);
    
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ 
        video: { facingMode: 'user' },
        audio: false 
      });
      
      setCameraStream(stream);
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
      }
      
      // Simulate face scanning progress
      const progressInterval = setInterval(() => {
        setScanProgress(prev => {
          if (prev >= 100) {
            clearInterval(progressInterval);
            return 100;
          }
          return prev + 10;
        });
      }, 200);
      
      // Complete scan after 2 seconds
      setTimeout(() => {
        completeFaceScan();
        if (progressInterval) {
          clearInterval(progressInterval);
        }
      }, 2000);
      
    } catch (error) {
      console.error('Camera access denied:', error);
      setFaceScanActive(false);
    }
  }, []);

  // Complete facial recognition
  const completeFaceScan = useCallback(() => {
    setFaceScanActive(false);
    
    // Stop camera
    if (cameraStream) {
      cameraStream.getTracks().forEach(track => track.stop());
      setCameraStream(null);
    }
    
    // Simulate AI face verification
    setKycResult({
      status: 'approved',
      riskScore: 0.15,
      verificationId: `KYC_${Date.now()}`,
      estimatedTime: 30,
      message: 'Identity verified successfully'
    });
    
    // Update step completion
    setDocuments(prev => prev.map(doc => 
      doc.id === 'passport' 
        ? { ...doc, verified: true }
        : doc
    ));
  }, [cameraStream]);

  // Submit KYC application
  const submitKYC = useCallback(async () => {
    setIsProcessing(true);
    setKycResult(prev => ({ ...prev, status: 'processing', estimatedTime: 60 }));
    
    // Simulate AI-powered KYC processing
    await new Promise(resolve => setTimeout(resolve, 3000));
    
    const riskScore = Math.random() * 0.3; // Low risk score
    const approved = riskScore < 0.25;
    
    setKycResult({
      status: approved ? 'approved' : 'rejected',
      riskScore,
      verificationId: `KYC_${Date.now()}`,
      estimatedTime: 30,
      message: approved 
        ? 'Identity verified successfully' 
        : 'Verification failed. Please contact support.'
    });
    
    setIsProcessing(false);
  }, []);

  // Handle step navigation
  const nextStep = useCallback(() => {
    if (currentStep < steps.length - 1) {
      setCurrentStep(prev => prev + 1);
    }
  }, [currentStep]);

  const prevStep = useCallback(() => {
    if (currentStep > 0) {
      setCurrentStep(prev => prev - 1);
    }
  }, [currentStep]);

  const goToStep = useCallback((stepIndex: number) => {
    setCurrentStep(stepIndex);
  }, []);

  // Calculate progress
  const progress = ((currentStep + 1) / steps.length) * 100;

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 text-white">
      {/* Progress Bar */}
      <div className="border-b border-slate-700 bg-slate-800/50 backdrop-blur-sm sticky top-0 z-50">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <h1 className="text-xl font-bold">Complete Your Profile</h1>
              <div className="text-sm text-slate-400">
                Step {currentStep + 1} of {steps.length}
              </div>
            </div>
            <div className="flex items-center space-x-2">
              <div className="text-sm text-slate-400">
                {Math.round(progress)}% Complete
              </div>
              <button
                onClick={() => window.location.href = '/login'}
                className="text-slate-400 hover:text-white transition-colors"
              >
                Sign In Instead
              </button>
            </div>
          </div>
          
          {/* Progress Bar */}
          <div className="mt-4 w-full bg-slate-700 rounded-full h-2">
            <motion.div
              className="h-full bg-gradient-to-r from-blue-500 to-purple-600 rounded-full"
              initial={{ width: 0 }}
              animate={{ width: `${progress}%` }}
              transition={{ duration: 0.5 }}
            />
          </div>
        </div>
      </div>

      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Steps Sidebar */}
          <div className="lg:col-span-1">
            <div className="space-y-4">
              {steps.map((step, index) => (
                <motion.button
                  key={step.id}
                  onClick={() => goToStep(index)}
                  className={`w-full text-left p-4 rounded-lg border transition-all ${
                    index === currentStep 
                      ? 'bg-blue-500/20 border-blue-500' 
                      : step.completed 
                        ? 'bg-green-500/20 border-green-500' 
                        : 'bg-slate-800 border-slate-700 hover:border-slate-600'
                  }`}
                  disabled={index > currentStep}
                >
                  <div className="flex items-center space-x-3">
                    <div className={`p-2 rounded-lg ${
                      index === currentStep 
                        ? 'bg-blue-500 text-white' 
                        : step.completed 
                          ? 'bg-green-500 text-white' 
                          : 'bg-slate-700 text-slate-400'
                      }`}>
                      {step.icon}
                    </div>
                    <div className="flex-1">
                      <div className="font-medium">{step.title}</div>
                      <div className="text-sm opacity-70">{step.description}</div>
                    </div>
                    {step.completed && (
                      <CheckCircle className="w-5 h-5 text-green-500" />
                    )}
                  </div>
                </motion.button>
              ))}
            </div>
          </div>

          {/* Main Content */}
          <div className="lg:col-span-2">
            <AnimatePresence mode="wait">
              <motion.div
                key={currentStep}
                initial={{ opacity: 0, x: 50 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -50 }}
                transition={{ duration: 0.3 }}
              >
                {/* Step 1: Account Creation */}
                {currentStep === 0 && (
                  <div className="bg-slate-800/50 border border-slate-700/50 rounded-xl p-8 backdrop-blur-sm">
                    <h2 className="text-2xl font-bold mb-6">Create Your Account</h2>
                    
                    <div className="space-y-6">
                      {/* Email */}
                      <div>
                        <label className="block text-sm font-medium text-slate-300 mb-2">
                          Email Address</label>
                        <div className="relative">
                          <Mail className="absolute left-3 top-3 w-5 h-5 text-slate-400" />
                          <input
                            type="email"
                            value={userData.email}
                            onChange={(e) => setUserData(prev => ({ ...prev, email: e.target.value }))}
                            className="w-full bg-slate-700 border border-slate-600 rounded-lg pl-12 pr-4 py-3 text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500"
                            placeholder="your@email.com"
                          />
                        </div>
                      </div>
                      
                      {/* Password */}
                      <div>
                        <label className="block text-sm font-medium text-slate-300 mb-2">
                          Password
                        </label>
                        <div className="relative">
                          <Lock className="absolute left-3 top-3 w-5 h-5 text-slate-400" />
                          <input
                            type={showPassword ? 'text' : 'password'}
                            value={userData.password}
                            onChange={(e) => setUserData(prev => ({ ...prev, password: e.target.value }))}
                            className="w-full bg-slate-700 border border-slate-600 rounded-lg pl-12 pr-12 py-3 text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500"
                            placeholder="Create a strong password"
                          />
                          <button
                            onClick={() => setShowPassword(!showPassword)}
                            className="absolute right-3 top-3 text-slate-400 hover:text-white"
                          >
                            {showPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                          </button>
                        </div>
                      </div>
                      
                      {/* Terms and Privacy */}
                      <div className="space-y-4">
                        <label className="flex items-center space-x-3 cursor-pointer">
                          <input
                            type="checkbox"
                            checked={userData.acceptTerms}
                            onChange={(e) => setUserData(prev => ({ ...prev, acceptTerms: e.target.checked }))}
                            className="w-4 h-4 text-blue-500 bg-slate-700 border-slate-600 rounded focus:ring-2 focus:ring-blue-500"
                          />
                          <span className="text-sm text-slate-300">
                            I agree to the <a href="#" className="text-blue-400 hover:text-blue-300">Terms of Service</a>
                          </span>
                        </label>
                        
                        <label className="flex items-center space-x-3 cursor-pointer">
                          <input
                            type="checkbox"
                            checked={userData.acceptPrivacy}
                            onChange={(e) => setUserData(prev => ({ ...prev, acceptPrivacy: e.target.checked }))}
                            className="w-4 h-4 text-blue-500 bg-slate-700 border-slate-600 rounded focus:ring-2 focus:ring-blue-500"
                          />
                          <span className="text-sm text-slate-300">
                            I agree to the <a href="#" className="text-blue-400 hover:text-blue-300">Privacy Policy</a>
                          </span>
                        </label>
                      </div>
                    </div>
                    
                    <button
                      onClick={nextStep}
                      disabled={!userData.email || !userData.password || !userData.acceptTerms || !userData.acceptPrivacy}
                      className="w-full bg-blue-500 hover:bg-blue-600 disabled:bg-slate-700 disabled:text-slate-500 text-white font-medium py-3 rounded-lg transition-colors"
                    >
                      Continue
                    </button>
                  </div>
                )}

                {/* Step 2: Personal Information */}
                {currentStep === 1 && (
                  <div className="bg-slate-800/50 border border-slate-700/50 rounded-xl p-8 backdrop-blur-sm">
                    <h2 className="text-2xl font-bold mb-6">Personal Information</h2>
                    
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                      <div>
                        <label className="block text-sm font-medium text-slate-300 mb-2">First Name</label>
                        <input
                          type="text"
                          value={userData.firstName}
                          onChange={(e) => setUserData(prev => ({ ...prev, firstName: e.target.value }))}
                          className="w-full bg-slate-700 border border-slate-600 rounded-lg px-4 py-3 text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500"
                          placeholder="John"
                        />
                      </div>
                      
                      <div>
                        <label className="block text-sm font-medium text-slate-300 mb-2">Last Name</label>
                        <input
                          type="text"
                          value={userData.lastName}
                          onChange={(e) => setUserData(prev => ({ ...prev, lastName: e.target.value }))}
                          className="w-full bg-slate-700 border border-slate-600 rounded-lg px-4 py-3 text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500"
                          placeholder="Doe"
                        />
                      </div>
                      
                      <div>
                        <label className="block text-sm font-medium text-slate-300 mb-2">Date of Birth</label>
                        <input
                          type="date"
                          value={userData.dateOfBirth}
                          onChange={(e) => setUserData(prev => ({ ...prev, dateOfBirth: e.target.value }))}
                          className="w-full bg-slate-700 border border-slate-600 rounded-lg px-4 py-3 text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                        />
                      </div>
                      
                      <div>
                        <label className="block text-sm font-medium text-slate-300 mb-2">Nationality</label>
                        <select
                          value={userData.nationality}
                          onChange={(e) => setUserData(prev => ({ ...prev, nationality: e.target.value }))}
                          className="w-full bg-slate-700 border border-slate-600 rounded-lg px-4 py-3 text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                        >
                          <option value="">Select nationality</option>
                          {supportedCountries.map(country => (
                            <option key={country} value={country}>{country}</option>
                          ))}
                        </select>
                      </div>
                      
                      <div>
                        <label className="block text-sm font-medium text-slate-300 mb-2">Phone Number</label>
                        <div className="relative">
                          <Smartphone className="absolute left-3 top-3 w-5 h-5 text-slate-400" />
                          <input
                            type="tel"
                            value={userData.phone}
                            onChange={(e) => setUserData(prev => ({ ...prev, phone: e.target.value }))}
                            className="w-full bg-slate-700 border border-slate-600 rounded-lg pl-12 pr-4 py-3 text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500"
                            placeholder="+1 (555) 123-4567"
                          />
                        </div>
                      </div>
                    </div>
                    
                    <div className="flex space-x-4">
                      <button
                        onClick={prevStep}
                        className="flex-1 bg-slate-700 hover:bg-slate-600 text-white font-medium py-3 rounded-lg transition-colors"
                      >
                        Back
                      </button>
                      <button
                        onClick={nextStep}
                        disabled={!userData.firstName || !userData.lastName || !userData.dateOfBirth || !userData.nationality}
                        className="flex-1 bg-blue-500 hover:bg-blue-600 disabled:bg-slate-700 disabled:text-slate-500 text-white font-medium py-3 rounded-lg transition-colors"
                      >
                        Continue
                      </button>
                    </div>
                  </div>
                )}

                {/* Step 3: Document Upload */}
                {currentStep === 2 && (
                  <div className="bg-slate-800/50 border border-slate-700/50 rounded-xl p-8 backdrop-blur-sm">
                    <h2 className="text-2xl font-bold mb-6">Document Verification</h2>
                    <p className="text-slate-400 mb-6">
                      Upload your documents for AI-powered verification. Our system will automatically detect 
                      document authenticity, tampering, and verify information in seconds.
                    </p>
                    
                    <div className="space-y-6">
                      {documents.map((doc, index) => (
                        <div key={doc.id} className="border border-slate-700 rounded-lg p-4">
                          <div className="flex items-center justify-between mb-4">
                            <div className="flex items-center space-x-3">
                              <Shield className="w-5 h-5 text-slate-400" />
                              <span className="font-medium">{doc.name}</span>
                            </div>
                            {doc.verified && (
                              <CheckCircle className="w-5 h-5 text-green-500" />
                            )}
                          </div>
                          
                          {doc.preview ? (
                            <div className="mb-4">
                              <img 
                                src={doc.preview} 
                                alt={doc.name}
                                className="w-full h-32 object-cover rounded-lg"
                              />
                            </div>
                          ) : (
                            <div className="border-2 border-dashed border-slate-600 rounded-lg p-8 text-center">
                              <Upload className="w-12 h-12 mx-auto mb-4 text-slate-400" />
                              <p className="text-slate-400 mb-4">
                                Click to upload {doc.name.toLowerCase()}
                              </p>
                              <input
                                ref={fileInputRef}
                                type="file"
                                accept="image/*,.pdf"
                                onChange={(e) => {
                                  const file = e.target.files?.[0];
                                  if (file) {
                                    handleFileUpload(doc.id, file);
                                  }
                                }}
                                className="hidden"
                                id={`file-${doc.id}`}
                              />
                              <label
                                htmlFor={`file-${doc.id}`}
                                className="cursor-pointer bg-blue-500 hover:bg-blue-600 text-white px-6 py-2 rounded-lg transition-colors"
                              >
                                {doc.uploaded ? 'Change Document' : 'Upload Document'}
                              </label>
                            </div>
                          )}
                          
                          {doc.uploaded && (
                            <div className="flex items-center space-x-2 text-sm">
                              {doc.verified ? (
                                <>
                                  <CheckCircle className="w-4 h-4 text-green-500" />
                                  <span className="text-green-400">Verified</span>
                                </>
                              ) : (
                                <>
                                  <AlertTriangle className="w-4 h-4 text-yellow-500" />
                                  <span className="text-yellow-400">Processing...</span>
                                </>
                              )}
                            </div>
                          )}
                          
                          {doc.error && (
                            <div className="mt-2 p-2 bg-red-500/20 border border-red-500/50 rounded text-red-400 text-sm">
                              {doc.error}
                            </div>
                          )}
                        </div>
                      ))}
                    </div>
                    
                    <div className="flex space-x-4">
                      <button
                        onClick={prevStep}
                        className="flex-1 bg-slate-700 hover:bg-slate-600 text-white font-medium py-3 rounded-lg transition-colors"
                      >
                        Back
                      </button>
                      <button
                        onClick={nextStep}
                        disabled={documents.filter(doc => doc.verified).length < 2}
                        className="flex-1 bg-blue-500 hover:bg-blue-600 disabled:bg-slate-700 disabled:text-slate-500 text-white font-medium py-3 rounded-lg transition-colors"
                      >
                        Continue
                      </button>
                    </div>
                  </div>
                )}

                {/* Step 4: Biometric Verification */}
                {currentStep === 3 && (
                  <div className="bg-slate-800/50 border border-slate-700/50 rounded-xl p-8 backdrop-blur-sm">
                    <h2 className="text-2xl font-bold mb-6">Biometric Verification</h2>
                    <p className="text-slate-400 mb-6">
                      Complete facial recognition for instant identity verification. This takes less than 10 seconds.
                    </p>
                    
                    {!faceScanActive && !kycResult.verificationId && (
                      <div className="text-center">
                        <div className="mb-8">
                          <Fingerprint className="w-16 h-16 mx-auto mb-4 text-blue-500" />
                          <h3 className="text-xl font-semibold mb-2">Ready for Face Scan</h3>
                          <p className="text-slate-400 mb-6">
                            Position your face in the camera and click start scan
                          </p>
                        </div>
                        
                        <button
                          onClick={startFaceScan}
                          className="bg-blue-500 hover:bg-blue-600 text-white font-medium px-8 py-3 rounded-lg transition-colors"
                        >
                          <Camera className="w-5 h-5 inline mr-2" />
                          Start Face Scan
                        </button>
                      </div>
                    )}
                    
                    {faceScanActive && (
                      <div className="text-center">
                        <div className="mb-4">
                          <video
                            ref={videoRef}
                            autoPlay
                            playsInline
                            muted
                            className="w-full max-w-md mx-auto rounded-lg bg-slate-900"
                          />
                          <canvas ref={canvasRef} className="hidden" />
                        </div>
                        
                        <div className="mb-4">
                          <div className="text-sm text-slate-400 mb-2">Scanning...</div>
                          <div className="w-full bg-slate-700 rounded-full h-2">
                            <motion.div
                              className="h-full bg-gradient-to-r from-blue-500 to-purple-600 rounded-full"
                              initial={{ width: 0 }}
                              animate={{ width: `${scanProgress}%` }}
                              transition={{ duration: 0.2 }}
                            />
                          </div>
                        </div>
                        
                        <div className="text-sm text-slate-400">
                          {scanProgress}% complete
                        </div>
                      </div>
                    </div>
                    )}
                    
                    {kycResult.verificationId && (
                      <div className="text-center">
                        <div className="mb-8">
                          {kycResult.status === 'approved' ? (
                            <>
                              <CheckCircle className="w-16 h-16 mx-auto mb-4 text-green-500" />
                              <h3 className="text-2xl font-semibold mb-2 text-green-400">Verification Complete!</h3>
                              <p className="text-slate-400 mb-6">
                                Your identity has been verified successfully. You now have full access to DEDAN 2.0.
                              </p>
                            </>
                          ) : (
                            <>
                              <AlertTriangle className="w-16 h-16 mx-auto mb-4 text-red-500" />
                              <h3 className="text-2xl font-semibold mb-2 text-red-400">Verification Failed</h3>
                              <p className="text-slate-400 mb-6">
                                {kycResult.message || 'Verification failed. Please contact support.'}
                              </p>
                            </>
                          )}
                        </div>
                        
                        <div className="bg-slate-700 rounded-lg p-4 mb-6">
                          <div className="grid grid-cols-2 gap-4 text-sm">
                            <div>
                              <div className="text-slate-400">Risk Score</div>
                              <div className={`text-lg font-semibold ${
                                kycResult.riskScore < 0.2 ? 'text-green-400' :
                                kycResult.riskScore < 0.5 ? 'text-yellow-400' : 'text-red-400'
                              }`}>
                                {(kycResult.riskScore * 100).toFixed(1)}%
                              </div>
                            </div>
                            <div>
                              <div className="text-slate-400">Verification ID</div>
                              <div className="text-lg font-semibold text-white">
                                {kycResult.verificationId}
                              </div>
                            </div>
                          </div>
                        </div>
                      </div>
                      
                      <button
                        onClick={() => window.location.href = '/dashboard'}
                        className="bg-green-500 hover:bg-green-600 text-white font-medium px-8 py-3 rounded-lg transition-colors"
                      >
                        Go to Dashboard
                      </button>
                    </div>
                  )}
                  </div>
                )}
              </motion.div>
            </AnimatePresence>
          </div>
        </div>
      </div>
    </div>
  );
};

export default OnboardingKYC;
