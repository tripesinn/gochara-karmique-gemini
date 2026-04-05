package com.karmicgochara.app;

import com.getcapacitor.BridgeActivity;

public class MainActivity extends BridgeActivity {

    @Override
    public void onCreate(android.os.Bundle savedInstanceState) {
        // Plugin Gemma 4 — inférence locale via MediaPipe Tasks GenAI
        registerPlugin(GemmaSynthesisPlugin.class);
        super.onCreate(savedInstanceState);
    }
}
