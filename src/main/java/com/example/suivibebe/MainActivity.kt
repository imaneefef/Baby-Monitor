package com.example.suivibebe

import android.Manifest
import android.app.NotificationChannel
import android.app.NotificationManager
import android.content.Context
import android.content.pm.PackageManager
import android.media.RingtoneManager
import android.os.Build
import android.os.Bundle
import android.util.Log
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.foundation.layout.*
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.core.app.NotificationCompat
import androidx.core.app.NotificationManagerCompat
import androidx.core.content.ContextCompat
import com.example.suivibebe.ui.theme.SuiviBebeTheme
import com.google.firebase.database.*

class MainActivity : ComponentActivity() {

    private lateinit var mDatabase: FirebaseDatabase
    private lateinit var mRef: DatabaseReference

    private val requestPermissionLauncher = registerForActivityResult(
        ActivityResultContracts.RequestPermission()
    ) { isGranted ->
        if (isGranted) {
            Log.d("Permission", "Notification permission granted")
        } else {
            Log.e("Permission", "Notification permission denied")
        }
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()

        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
            if (ContextCompat.checkSelfPermission(
                    this,
                    Manifest.permission.POST_NOTIFICATIONS
                ) != PackageManager.PERMISSION_GRANTED
            ) {
                requestPermissionLauncher.launch(Manifest.permission.POST_NOTIFICATIONS)
            }
        }

        mDatabase = FirebaseDatabase.getInstance()
        mRef = mDatabase.reference // Accès à la racine de la base de données

        setContent {
            SuiviBebeTheme {
                Scaffold(modifier = Modifier.fillMaxSize()) { innerPadding ->
                    Column(modifier = Modifier.padding(innerPadding)) {
                        FirebaseDataDisplay(mRef, this@MainActivity)
                    }
                }
            }
        }
    }

    fun sendNotification(context: Context, temperature: Float, humidity: Float) {
        val channelId = "baby_alerts"
        val notificationId = 1

        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
            if (ContextCompat.checkSelfPermission(
                    context,
                    Manifest.permission.POST_NOTIFICATIONS
                ) != PackageManager.PERMISSION_GRANTED
            ) {
                Log.e("Notification", "Permission refusée")
                return
            }
        }

        val builder = NotificationCompat.Builder(context, channelId)
            .setSmallIcon(R.drawable.baby_icon)
            .setContentTitle("🚨 Alerte bébé")
            .setContentText("Bébé pleure! Temp: ${temperature}°C, Humidité: ${humidity}%")
            .setPriority(NotificationCompat.PRIORITY_HIGH)
            .setAutoCancel(true)
            .setSound(RingtoneManager.getDefaultUri(RingtoneManager.TYPE_ALARM))

        val notificationManager =
            context.getSystemService(Context.NOTIFICATION_SERVICE) as NotificationManager

        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            val channel = NotificationChannel(
                channelId,
                "Baby Alerts",
                NotificationManager.IMPORTANCE_HIGH
            )
            notificationManager.createNotificationChannel(channel)
        }

        NotificationManagerCompat.from(context).notify(notificationId, builder.build())
    }
}

@Composable
fun FirebaseDataDisplay(mRef: DatabaseReference, context: Context) {
    var temperature by remember { mutableStateOf(0f) }
    var humidity by remember { mutableStateOf(0f) }
    var isCrying by remember { mutableStateOf(false) }

    LaunchedEffect(mRef) {
        mRef.addValueEventListener(object : ValueEventListener {
            override fun onDataChange(snapshot: DataSnapshot) {
                temperature = snapshot.child("environment/temperature").getValue(Float::class.java) ?: 0f
                humidity = snapshot.child("environment/humidity").getValue(Float::class.java) ?: 0f
                val newIsCrying = snapshot.child("babyStatus/isCrying").getValue(Boolean::class.java) ?: false

                if (newIsCrying && !isCrying) {
                    (context as? MainActivity)?.sendNotification(context, temperature, humidity)
                }

                isCrying = newIsCrying
            }

            override fun onCancelled(error: DatabaseError) {
                Log.e("Firebase", "Erreur lecture données", error.toException())
            }
        })
    }

    Column(modifier = Modifier.padding(16.dp)) {
        Text(text = "👶 Baby Monitor", fontSize = 24.sp, color = Color.DarkGray)

        InfoCard("🌡️ Température", "$temperature°C", Color(0xFFFFA726))
        InfoCard("💧 Humidité", "$humidity%", Color(0xFF42A5F5))

        val cryingStatus = if (isCrying) "Bébé pleure !" else "Bébé calme"
        val cryingColor = if (isCrying) Color(0xFFEF5350) else Color(0xFF66BB6A)
        InfoCard("État", cryingStatus, cryingColor)
    }
}