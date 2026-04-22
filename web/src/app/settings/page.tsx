"use client";

import { useEffect, useRef } from "react";

import { CPAPoolDialog } from "./components/cpa-pool-dialog";
import { CPAPoolsCard } from "./components/cpa-pools-card";
import { ImportBrowserDialog } from "./components/import-browser-dialog";
import { ProxySettingsCard } from "./components/proxy-settings-card";
import { SettingsHeader } from "./components/settings-header";
import { useSettingsStore } from "./store";

function SettingsDataController() {
  const didLoadRef = useRef(false);
  const initialize = useSettingsStore((state) => state.initialize);
  const loadPools = useSettingsStore((state) => state.loadPools);
  const pools = useSettingsStore((state) => state.pools);

  useEffect(() => {
    if (didLoadRef.current) {
      return;
    }
    didLoadRef.current = true;
    void initialize();
  }, [initialize]);

  useEffect(() => {
    const hasRunningJobs = pools.some((pool) => {
      const status = pool.import_job?.status;
      return status === "pending" || status === "running";
    });
    if (!hasRunningJobs) {
      return;
    }

    const timer = window.setInterval(() => {
      void loadPools(true);
    }, 1500);
    return () => window.clearInterval(timer);
  }, [loadPools, pools]);

  return null;
}

export default function SettingsPage() {
  return (
    <>
      <SettingsDataController />
      <SettingsHeader />
      <section className="space-y-6">
        <ProxySettingsCard />
        <CPAPoolsCard />
      </section>
      <CPAPoolDialog />
      <ImportBrowserDialog />
    </>
  );
}
