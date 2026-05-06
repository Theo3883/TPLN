import { useEffect, useState } from 'react';
import * as api from './api';
import { editionsToBooks } from './transformers';

export function useEditions(limit = 90) {
  const [data, setData] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    let mounted = true;
    setLoading(true);
    api.listEditions(limit)
      .then((res: any) => {
        if (!mounted) return;
        const list = Array.isArray(res) ? res : res.items ?? [];
        setData(editionsToBooks(list));
      })
      .catch((err: Error) => {
        if (!mounted) return;
        setError(err);
      })
      .finally(() => {
        if (!mounted) return;
        setLoading(false);
      });

    return () => {
      mounted = false;
    };
  }, [limit]);

  return { data, loading, error };
}

export async function fetchEdition(id: string | number) {
  const res = await api.getEdition(id);
  return res;
}

export async function fetchReviewsForEdition(id: string | number) {
  const res = await api.getEditionReviews(id);
  return res;
}

export default {
  useEditions,
  fetchEdition,
  fetchReviewsForEdition,
};
