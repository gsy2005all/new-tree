import { useRef, useState } from "react";
import {
  ActivityIndicator,
  BackHandler,
  Platform,
  SafeAreaView,
  StyleSheet,
  View,
} from "react-native";
import { StatusBar } from "expo-status-bar";
import { WebView } from "react-native-webview";

// ⚠️ 改成你电脑的局域网地址（和手机连同一个 WiFi），后端用 `python main.py` 启动
// 默认直接进「用户入口」；想进管理端改成 .../static/admin.html，想要入口选择页改成 .../
const SITE_URL = "http://192.168.1.64:8000/static/user.html";

export default function App() {
  const webRef = useRef(null);
  const [loading, setLoading] = useState(true);
  const [canGoBack, setCanGoBack] = useState(false);

  // 安卓物理返回键：网页能后退就后退，否则交给系统
  if (Platform.OS === "android") {
    BackHandler.addEventListener("hardwareBackPress", () => {
      if (canGoBack && webRef.current) {
        webRef.current.goBack();
        return true;
      }
      return false;
    });
  }

  return (
    <SafeAreaView style={styles.container}>
      <StatusBar style="light" backgroundColor="#2f8f4e" />
      <WebView
        ref={webRef}
        source={{ uri: SITE_URL }}
        onLoadEnd={() => setLoading(false)}
        onNavigationStateChange={(nav) => setCanGoBack(nav.canGoBack)}
        startInLoadingState
        domStorageEnabled
        javaScriptEnabled
        style={styles.web}
      />
      {loading && (
        <View style={styles.loaderBox} pointerEvents="none">
          <ActivityIndicator size="large" color="#2f8f4e" />
        </View>
      )}
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: "#2f8f4e" },
  web: { flex: 1, backgroundColor: "#f4f6f8" },
  loaderBox: {
    ...StyleSheet.absoluteFillObject,
    alignItems: "center",
    justifyContent: "center",
  },
});
