import { createBottomTabNavigator } from "@react-navigation/bottom-tabs"
import { NavigationContainer } from "@react-navigation/native"
import { View, Text } from "react-native"
import { DashboardScreen } from "@/screens/DashboardScreen"
import { TransactionsScreen } from "@/screens/TransactionsScreen"
import { SearchScreen } from "@/screens/SearchScreen"
import { RecurringScreen } from "@/screens/RecurringScreen"
import { useThemeStore } from "@/stores/useThemeStore"

const Tab = createBottomTabNavigator()

const tabIcons: Record<string, { active: string; inactive: string }> = {
  Dashboard: { active: "📊", inactive: "📊" },
  Transactions: { active: "💳", inactive: "💳" },
  Search: { active: "🔍", inactive: "🔍" },
  Recurring: { active: "🔄", inactive: "🔄" },
}

function TabIcon({ routeName, focused }: { routeName: string; focused: boolean }) {
  const icon = tabIcons[routeName]
  if (!icon) return null

  return (
    <View className="items-center justify-center">
      <Text className={focused ? "text-xl" : "text-lg opacity-50"}>{icon?.active || ""}</Text>
    </View>
  )
}

export function Navigation() {
  const isDark = useThemeStore((s) => s.isDark)

  return (
    <NavigationContainer
      theme={{
        dark: isDark,
        colors: {
          primary: "#007aff",
          background: isDark ? "#0a0a0f" : "#ffffff",
          card: isDark ? "#14141f" : "#f8f8fa",
          text: isDark ? "#f5f5f7" : "#0a0a0f",
          border: isDark ? "#2c2c3a" : "#e5e5ea",
          notification: "#ff3b30",
        },
        fonts: {
          regular: { fontFamily: "System", fontWeight: "400" },
          medium: { fontFamily: "System", fontWeight: "500" },
          bold: { fontFamily: "System", fontWeight: "700" },
          heavy: { fontFamily: "System", fontWeight: "800" },
        },
      }}
    >
      <Tab.Navigator
        screenOptions={({ route }) => ({
          headerShown: false,
          tabBarIcon: ({ focused }) => <TabIcon routeName={route.name} focused={focused} />,
          tabBarActiveTintColor: "#007aff",
          tabBarInactiveTintColor: "#8e8e93",
          tabBarStyle: {
            backgroundColor: isDark ? "#14141f" : "#ffffff",
            borderTopColor: isDark ? "#2c2c3a" : "#e5e5ea",
            borderTopWidth: 0.5,
            paddingBottom: 8,
            paddingTop: 6,
            height: 60,
          },
          tabBarLabelStyle: {
            fontSize: 11,
            fontWeight: "600",
          },
        })}
      >
        <Tab.Screen
          name="Dashboard"
          component={DashboardScreen}
          options={{ tabBarLabel: "Home" }}
        />
        <Tab.Screen
          name="Transactions"
          component={TransactionsScreen}
          options={{ tabBarLabel: "Activity" }}
        />
        <Tab.Screen
          name="Search"
          component={SearchScreen}
          options={{ tabBarLabel: "Search" }}
        />
        <Tab.Screen
          name="Recurring"
          component={RecurringScreen}
          options={{ tabBarLabel: "Bills" }}
        />
      </Tab.Navigator>
    </NavigationContainer>
  )
}
