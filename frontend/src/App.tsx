/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Layout from './components/layout/Layout';
import Home from './pages/Home';
import Catalog from './pages/Catalog';
import Search from './pages/Search';
import Moderation from './pages/Moderation';
import Rankings from './pages/Rankings';
import EditionDetail from './pages/EditionDetail';

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<Home />} />
          <Route path="catalog" element={<Catalog />} />
          <Route path="search" element={<Search />} />
          <Route path="moderation" element={<Moderation />} />
          <Route path="rankings" element={<Rankings />} />
          <Route path="edition/:id" element={<EditionDetail />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

