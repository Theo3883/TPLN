/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext';
import Layout from './components/layout/Layout';
import ProtectedRoute from './components/ProtectedRoute';
import Home from './pages/Home';
import Catalog from './pages/Catalog';
import Search from './pages/Search';
import Moderation from './pages/Moderation';
import Rankings from './pages/Rankings';
import EditionDetail from './pages/EditionDetail';
import Login from './pages/Login';
import Register from './pages/Register';
import BookPreviews from './pages/BookPreviews';
import BookPreviewDetail from './pages/BookPreviewDetail';
import MyGiftBooks from './pages/MyGiftBooks';

export default function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <Routes>
          <Route path="/" element={<Layout />}>
            <Route index element={<Home />} />
            <Route path="catalog" element={<Catalog />} />
            <Route path="book-previews" element={<BookPreviews />} />
            <Route path="book-previews/:slug" element={<BookPreviewDetail />} />
            <Route path="my-gift-books" element={<MyGiftBooks />} />
            <Route path="search" element={<Search />} />
            <Route path="rankings" element={<Rankings />} />
            <Route path="edition/:id" element={<EditionDetail />} />
            <Route path="login" element={<Login />} />
            <Route path="register" element={<Register />} />
            <Route
              path="moderation"
              element={
                <ProtectedRoute>
                  <Moderation />
                </ProtectedRoute>
              }
            />
          </Route>
        </Routes>
      </AuthProvider>
    </BrowserRouter>
  );
}

