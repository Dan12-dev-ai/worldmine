// ISO 20022 Messaging Standard Implementation
// Ensures interoperability with global banking systems
// ISO/IEC 25010 - Interoperability & Portability Compliance

import { v4 as uuidv4 } from 'uuid';

// ISO 2002-2.0 Core Components
export interface PartyIdentification {
  id: string;
  idType: 'BIC' | 'IBAN' | 'PAN' | 'OTH';
  issuer?: string;
  name?: string;
  postalAddress?: PostalAddress;
  countryOfResidence?: string;
  contactDetails?: ContactDetails;
}

export interface PostalAddress {
  streetName?: string;
  buildingName?: string;
  buildingNumber?: string;
  postCode?: string;
  townName?: string;
  countrySubDivision?: string;
  country: string;
}

export interface ContactDetails {
  name?: string;
  phoneNumber?: string;
  mobilePhoneNumber?: string;
  faxNumber?: string;
  emailAddress?: string;
  other?: Array<{
    type: string;
    value: string;
  }>;
}

export interface Amount {
  value: string; // Decimal as string to avoid floating point issues
  currency: string; // ISO 4217 currency code
}

export interface ChargeBearer {
  code: 'SHAR' | 'DEBT' | 'CRED' | 'SLEV';
}

export interface Purpose {
  code?: string; // ISO 20022 purpose code
  proprietary?: string;
}

export interface PaymentIdentification {
  instructionId?: string;
  endToEndId?: string;
  transactionId?: string;
  mandateId?: string;
  chequeNumber?: string;
  clearingSystemReference?: string;
}

export interface PaymentInformation {
  paymentId: PaymentIdentification;
  amount: Amount;
  chargeBearer: ChargeBearer;
  creditor: PartyIdentification;
  debtor: PartyIdentification;
  creditorAgent?: PartyIdentification;
  debtorAgent?: PartyIdentification;
  purpose?: Purpose;
  requestedExecutionDate?: string;
  ultimateDebtor?: PartyIdentification;
  ultimateCreditor?: PartyIdentification;
  interbankSettlementDate?: string;
  settlementMethod?: 'CLRG' | 'COVER' | 'SDVA' | 'INGA' | 'CHIP';
}

export interface GroupHeader {
  messageId: string;
  creationDateTime: string;
  numberOfTransactions: number;
  totalAmount?: Amount;
  initiatingParty: PartyIdentification;
  forwardingAgent?: PartyIdentification;
}

export interface SupplementaryData {
  envelope?: {
    data: any;
    schema?: string;
  };
  atmTransactionContext?: {
    data: any;
    schema?: string;
  };
  pointOfSaleContext?: {
    data: any;
    schema?: string;
  };
  eCommContext?: {
    data: any;
    schema?: string;
  };
}

// Main ISO 20022 Message Structure
export interface ISO20022Message {
  header: {
    messageIdentification: string;
    creationDateTime: string;
    initiatingParty: PartyIdentification;
    forwardingAgent?: PartyIdentification;
  };
  body: {
    groupHeader: GroupHeader;
    paymentInformation: PaymentInformation[];
    supplementaryData?: SupplementaryData;
  };
  metadata: {
    version: string;
    format: string;
    timestamp: string;
    messageId: string;
    correlationId?: string;
  };
}

// ISO 20022 Purpose Codes (Common financial purposes)
export const ISO20022_PURPOSE_CODES = {
  ACCT: 'Account Management',
  AGRT: 'Agricultural Settlement',
  ALIM: 'Alimony',
  ANNU: 'Annuity',
  BEXP: 'Business Expenses',
  CASH: 'Cash Management',
  CHAR: 'Charitable Donations',
  CORT: 'Trade Settlement',
  DIVI: 'Dividend',
  DVPM: 'Dividend Payment',
  EPAY: 'Electronic Payment',
  FCOL: 'Collection Fee',
  GOVT: 'Government Payment',
  INTC: 'Intra-Company Payment',
  INVS: 'Investment Management',
  LIMA: 'Life Insurance Premium',
  NETT: 'Netting',
  OTHR: 'Other',
  PEND: 'Pending Transaction',
  PENO: 'Penalty',
  PPTD: 'Postage',
  PRIA: 'Private Payment',
  REPA: 'Repair',
  SALA: 'Salary',
  SECU: 'Securities',
  SSBE: 'Social Security Benefit',
  TRAD: 'Trade Payment',
  VATX: 'VAT Payment'
} as const;

// ISO 20022 Charge Bearer Codes
export const ISO20022_CHARGE_BEARER_CODES = {
  SHAR: 'Shared',
  DEBT: 'Debtor',
  CRED: 'Creditor',
  SLEV: 'Service Level'
} as const;

// ISO 20022 Settlement Methods
export const ISO20022_SETTLEMENT_METHODS = {
  CLRG: 'Clearing',
  COVER: 'Cover Payment',
  SDVA: 'Same Day Value',
  INGA: 'Intra-bank',
  CHIP: 'Chip Card'
} as const;

// ISO 20022 Message Builder
export class ISO20022MessageBuilder {
  private message: Partial<ISO20022Message> = {
    metadata: {
      version: '2.0',
      format: 'iso.20022.pain.001.001.03',
      timestamp: new Date().toISOString(),
      messageId: uuidv4()
    }
  };

  // Set message header
  setHeader(initiatingParty: PartyIdentification, forwardingAgent?: PartyIdentification): this {
    this.message.header = {
      messageIdentification: uuidv4(),
      creationDateTime: new Date().toISOString(),
      initiatingParty,
      forwardingAgent
    };
    return this;
  }

  // Set group header
  setGroupHeader(numberOfTransactions: number, totalAmount?: Amount): this {
    if (!this.message.header) {
      throw new Error('Header must be set before group header');
    }

    this.message.body = {
      groupHeader: {
        messageId: uuidv4(),
        creationDateTime: new Date().toISOString(),
        numberOfTransactions,
        totalAmount,
        initiatingParty: this.message.header.initiatingParty
      },
      paymentInformation: []
    };
    return this;
  }

  // Add payment information
  addPayment(payment: PaymentInformation): this {
    if (!this.message.body) {
      throw new Error('Group header must be set before adding payments');
    }

    this.message.body.paymentInformation.push(payment);
    this.message.body.groupHeader.numberOfTransactions = this.message.body.paymentInformation.length;

    // Recalculate total amount
    if (this.message.body.paymentInformation.length > 0) {
      const totalValue = this.message.body.paymentInformation.reduce((sum, p) => {
        return sum + parseFloat(p.amount.value);
      }, 0);
      
      this.message.body.groupHeader.totalAmount = {
        value: totalValue.toFixed(2),
        currency: this.message.body.paymentInformation[0].amount.currency
      };
    }

    return this;
  }

  // Set supplementary data
  setSupplementaryData(data: SupplementaryData): this {
    if (!this.message.body) {
      throw new Error('Group header must be set before adding supplementary data');
    }

    this.message.body.supplementaryData = data;
    return this;
  }

  // Build final message
  build(): ISO20022Message {
    if (!this.message.header || !this.message.body) {
      throw new Error('Header and body must be set before building message');
    }

    if (this.message.body.paymentInformation.length === 0) {
      throw new Error('At least one payment must be added');
    }

    return this.message as ISO20022Message;
  }

  // Reset builder
  reset(): this {
    this.message = {
      metadata: {
        version: '2.0',
        format: 'iso.20022.pain.001.001.03',
        timestamp: new Date().toISOString(),
        messageId: uuidv4()
      }
    };
    return this;
  }
}

// Helper functions for creating ISO 20022 components
export const createPartyIdentification = (
  id: string,
  name: string,
  country: string,
  options?: {
    idType?: PartyIdentification['idType'];
    issuer?: string;
    postalAddress?: Partial<PostalAddress>;
    contactDetails?: Partial<ContactDetails>;
  }
): PartyIdentification => ({
  id,
  idType: options?.idType || 'OTH',
  issuer: options?.issuer,
  name,
  postalAddress: options?.postalAddress ? {
    country,
    ...options.postalAddress
  } : {
    country
  },
  countryOfResidence: country,
  contactDetails: options?.contactDetails
});

export const createAmount = (value: number, currency: string): Amount => ({
  value: value.toFixed(2),
  currency: currency.toUpperCase()
});

export const createPaymentIdentification = (
  instructionId?: string,
  endToEndId?: string,
  transactionId?: string
): PaymentIdentification => ({
  instructionId: instructionId || uuidv4(),
  endToEndId: endToEndId || uuidv4(),
  transactionId: transactionId || uuidv4()
});

// Transaction to ISO 20022 converter
export class TransactionToISO20022Converter {
  static convert(
    transaction: {
      id: string;
      amount: number;
      currency: string;
      debtor: {
        id: string;
        name: string;
        email?: string;
        phone?: string;
        address?: {
          street?: string;
          city?: string;
          country: string;
          postalCode?: string;
        };
      };
      creditor: {
        id: string;
        name: string;
        email?: string;
        phone?: string;
        address?: {
          street?: string;
          city?: string;
          country: string;
          postalCode?: string;
        };
      };
      purpose?: string;
      executionDate?: string;
    }
  ): ISO20022Message {
    const builder = new ISO20022MessageBuilder();

    // Create party identifications
    const debtorParty = createPartyIdentification(
      transaction.debtor.id,
      transaction.debtor.name,
      transaction.debtor.address?.country || 'ET',
      {
        idType: 'OTH',
        postalAddress: transaction.debtor.address ? {
          streetName: transaction.debtor.address.street,
          townName: transaction.debtor.address.city,
          postCode: transaction.debtor.address.postalCode
        } : undefined,
        contactDetails: {
          emailAddress: transaction.debtor.email,
          phoneNumber: transaction.debtor.phone
        }
      }
    );

    const creditorParty = createPartyIdentification(
      transaction.creditor.id,
      transaction.creditor.name,
      transaction.creditor.address?.country || 'ET',
      {
        idType: 'OTH',
        postalAddress: transaction.creditor.address ? {
          streetName: transaction.creditor.address.street,
          townName: transaction.creditor.address.city,
          postCode: transaction.creditor.address.postalCode
        } : undefined,
        contactDetails: {
          emailAddress: transaction.creditor.email,
          phoneNumber: transaction.creditor.phone
        }
      }
    );

    // Build message
    return builder
      .setHeader(debtorParty)
      .setGroupHeader(1, createAmount(transaction.amount, transaction.currency))
      .addPayment({
        paymentId: createPaymentIdentification(transaction.id),
        amount: createAmount(transaction.amount, transaction.currency),
        chargeBearer: { code: 'SHAR' },
        debtor: debtorParty,
        creditor: creditorParty,
        purpose: transaction.purpose ? {
          code: transaction.purpose as keyof typeof ISO20022_PURPOSE_CODES
        } : undefined,
        requestedExecutionDate: transaction.executionDate
      })
      .setSupplementaryData({
        eCommContext: {
          data: {
            originalTransactionId: transaction.id,
            platform: 'Worldmine',
            timestamp: new Date().toISOString()
          },
          schema: 'worldmine.transaction.v1'
        }
      })
      .build();
  }

  // Convert multiple transactions
  static convertBatch(
    transactions: Array<{
      id: string;
      amount: number;
      currency: string;
      debtor: {
        id: string;
        name: string;
        email?: string;
        phone?: string;
        address?: {
          street?: string;
          city?: string;
          country: string;
          postalCode?: string;
        };
      };
      creditor: {
        id: string;
        name: string;
        email?: string;
        phone?: string;
        address?: {
          street?: string;
          city?: string;
          country: string;
          postalCode?: string;
        };
      };
      purpose?: string;
      executionDate?: string;
    }>
  ): ISO20022Message {
    if (transactions.length === 0) {
      throw new Error('At least one transaction is required');
    }

    const builder = new ISO20022MessageBuilder();
    const firstTransaction = transactions[0];

    // Create initiating party
    const initiatingParty = createPartyIdentification(
      firstTransaction.debtor.id,
      firstTransaction.debtor.name,
      firstTransaction.debtor.address?.country || 'ET'
    );

    // Calculate total amount
    const totalAmount = transactions.reduce((sum, t) => sum + t.amount, 0);

    // Start building
    builder
      .setHeader(initiatingParty)
      .setGroupHeader(transactions.length, createAmount(totalAmount, firstTransaction.currency));

    // Add each transaction as payment
    for (const transaction of transactions) {
      const debtorParty = createPartyIdentification(
        transaction.debtor.id,
        transaction.debtor.name,
        transaction.debtor.address?.country || 'ET',
        {
          idType: 'OTH',
          postalAddress: transaction.debtor.address ? {
            streetName: transaction.debtor.address.street,
            townName: transaction.debtor.address.city,
            postCode: transaction.debtor.address.postalCode
          } : undefined,
          contactDetails: {
            emailAddress: transaction.debtor.email,
            phoneNumber: transaction.debtor.phone
          }
        }
      );

      const creditorParty = createPartyIdentification(
        transaction.creditor.id,
        transaction.creditor.name,
        transaction.creditor.address?.country || 'ET',
        {
          idType: 'OTH',
          postalAddress: transaction.creditor.address ? {
            streetName: transaction.creditor.address.street,
            townName: transaction.creditor.address.city,
            postCode: transaction.creditor.address.postalCode
          } : undefined,
          contactDetails: {
            emailAddress: transaction.creditor.email,
            phoneNumber: transaction.creditor.phone
          }
        }
      );

      builder.addPayment({
        paymentId: createPaymentIdentification(transaction.id),
        amount: createAmount(transaction.amount, transaction.currency),
        chargeBearer: { code: 'SHAR' },
        debtor: debtorParty,
        creditor: creditorParty,
        purpose: transaction.purpose ? {
          code: transaction.purpose as keyof typeof ISO20022_PURPOSE_CODES
        } : undefined,
        requestedExecutionDate: transaction.executionDate
      });
    }

    return builder.build();
  }
}

// ISO 20022 Message Validator
export class ISO20022Validator {
  static validate(message: ISO20022Message): {
    isValid: boolean;
    errors: string[];
    warnings: string[];
  } {
    const errors: string[] = [];
    const warnings: string[] = [];

    // Validate header
    if (!message.header) {
      errors.push('Header is required');
    } else {
      if (!message.header.messageIdentification) {
        errors.push('Message identification is required');
      }
      if (!message.header.creationDateTime) {
        errors.push('Creation date time is required');
      }
      if (!message.header.initiatingParty) {
        errors.push('Initiating party is required');
      }
    }

    // Validate body
    if (!message.body) {
      errors.push('Body is required');
    } else {
      // Validate group header
      if (!message.body.groupHeader) {
        errors.push('Group header is required');
      } else {
        if (!message.body.groupHeader.messageId) {
          errors.push('Group header message ID is required');
        }
        if (message.body.groupHeader.numberOfTransactions <= 0) {
          errors.push('Number of transactions must be positive');
        }
        if (!message.body.groupHeader.initiatingParty) {
          errors.push('Group header initiating party is required');
        }
      }

      // Validate payment information
      if (!message.body.paymentInformation || message.body.paymentInformation.length === 0) {
        errors.push('At least one payment information is required');
      } else {
        message.body.paymentInformation.forEach((payment, index) => {
          if (!payment.paymentId) {
            errors.push(`Payment ${index + 1}: Payment ID is required`);
          }
          if (!payment.amount) {
            errors.push(`Payment ${index + 1}: Amount is required`);
          } else {
            if (!payment.amount.value) {
              errors.push(`Payment ${index + 1}: Amount value is required`);
            }
            if (!payment.amount.currency) {
              errors.push(`Payment ${index + 1}: Amount currency is required`);
            }
            if (!/^[A-Z]{3}$/.test(payment.amount.currency)) {
              warnings.push(`Payment ${index + 1}: Currency code should be 3 uppercase letters`);
            }
          }
          if (!payment.chargeBearer) {
            errors.push(`Payment ${index + 1}: Charge bearer is required`);
          }
          if (!payment.creditor) {
            errors.push(`Payment ${index + 1}: Creditor is required`);
          }
          if (!payment.debtor) {
            errors.push(`Payment ${index + 1}: Debtor is required`);
          }
        });
      }
    }

    // Validate metadata
    if (!message.metadata) {
      warnings.push('Metadata is recommended');
    } else {
      if (!message.metadata.version) {
        warnings.push('Metadata version is recommended');
      }
      if (!message.metadata.format) {
        warnings.push('Metadata format is recommended');
      }
      if (!message.metadata.timestamp) {
        warnings.push('Metadata timestamp is recommended');
      }
      if (!message.metadata.messageId) {
        warnings.push('Metadata message ID is recommended');
      }
    }

    return {
      isValid: errors.length === 0,
      errors,
      warnings
    };
  }

  static validateParty(party: PartyIdentification): {
    isValid: boolean;
    errors: string[];
    warnings: string[];
  } {
    const errors: string[] = [];
    const warnings: string[] = [];

    if (!party.id) {
      errors.push('Party ID is required');
    }
    if (!party.country) {
      errors.push('Party country is required');
    }
    if (!party.countryOfResidence) {
      warnings.push('Country of residence is recommended');
    }

    return {
      isValid: errors.length === 0,
      errors,
      warnings
    };
  }
}

// ISO 20022 Message Serializer
export class ISO20022Serializer {
  static toJSON(message: ISO20022Message): string {
    return JSON.stringify(message, null, 2);
  }

  static fromJSON(json: string): ISO20022Message {
    const parsed = JSON.parse(json);
    
    // Validate structure
    const validation = ISO20022Validator.validate(parsed);
    if (!validation.isValid) {
      throw new Error(`Invalid ISO 20022 message: ${validation.errors.join(', ')}`);
    }

    return parsed as ISO20022Message;
  }

  static toXML(message: ISO20022Message): string {
    // Simplified XML generation (in production, use proper XML library)
    const xml = `<?xml version="1.0" encoding="UTF-8"?>
<Document xmlns="urn:iso:std:iso:20022:tech:xsd:pain.001.001.03">
  <CstmrCdtTrfInitn>
    <GrpHdr>
      <MsgId>${message.header.messageIdentification}</MsgId>
      <CreDtTm>${message.header.creationDateTime}</CreDtTm>
      <NbOfTxs>${message.body.groupHeader.numberOfTransactions}</NbOfTxs>
      <InitgPty>
        <Nm>${message.header.initiatingParty.name}</Nm>
        <Id>${message.header.initiatingParty.id}</Id>
      </InitgPty>
    </GrpHdr>
    ${message.body.paymentInformation.map(payment => `
    <PmtInf>
      <PmtId>
        <InstrId>${payment.paymentId.instructionId}</InstrId>
        <EndToEndId>${payment.paymentId.endToEndId}</EndToEndId>
      </PmtId>
      <Amt>
        <InstdAmt Ccy="${payment.amount.currency}">${payment.amount.value}</InstdAmt>
      </Amt>
      <ChrgBr>${payment.chargeBearer.code}</ChrgBr>
      <CdtrAgt>
        <FinInstnId>
          <Nm>${payment.creditor.name}</Nm>
          <Id>${payment.creditor.id}</Id>
        </FinInstnId>
      </CdtrAgt>
      <Cdtr>
        <Nm>${payment.creditor.name}</Nm>
      </Cdtr>
      <DbtrAgt>
        <FinInstnId>
          <Nm>${payment.debtor.name}</Nm>
          <Id>${payment.debtor.id}</Id>
        </FinInstnId>
      </DbtrAgt>
      <Dbtr>
        <Nm>${payment.debtor.name}</Nm>
      </Dbtr>
    </PmtInf>`).join('')}
  </CstmrCdtTrfInitn>
</Document>`;

    return xml;
  }
}

// Export all components
export default {
  ISO20022MessageBuilder,
  TransactionToISO20022Converter,
  ISO20022Validator,
  ISO20022Serializer,
  ISO20022_PURPOSE_CODES,
  ISO20022_CHARGE_BEARER_CODES,
  ISO20022_SETTLEMENT_METHODS,
  createPartyIdentification,
  createAmount,
  createPaymentIdentification
};
