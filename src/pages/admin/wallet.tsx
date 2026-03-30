import React from 'react';
import AdminWallet from '../../components/AdminWallet';
import ProtectedAdminRoute from '../../components/ProtectedAdminRoute';

const AdminWalletPage: React.FC = () => {
  return (
    <ProtectedAdminRoute>
      <AdminWallet />
    </ProtectedAdminRoute>
  );
};

export default AdminWalletPage;
