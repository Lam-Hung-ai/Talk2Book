"use client";

import { useCallback, useEffect, useState } from "react";

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://127.0.0.1:8000/api/v1";

export type CategoryOption = {
  id: string;
  value: string;
  description: string | null;
};

/** Fetch active category values for a given group_name */
export function useCategories(groupName: string) {
  const [options, setOptions] = useState<CategoryOption[]>([]);
  const [loading, setLoading] = useState(false);

  const load = useCallback(async () => {
    if (!groupName) return;
    setLoading(true);
    try {
      const res = await fetch(
        `${API_BASE_URL}/category/?group_name=${encodeURIComponent(groupName)}&is_active=true&page_size=200`
      );
      if (res.ok) {
        const data = (await res.json()) as { items: CategoryOption[] };
        setOptions(data.items ?? []);
      }
    } finally {
      setLoading(false);
    }
  }, [groupName]);

  useEffect(() => { void load(); }, [load]);

  return { options, loading, reload: load };
}
